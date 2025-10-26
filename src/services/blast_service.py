import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Bio import Entrez
from Bio.Blast import NCBIWWW, NCBIXML

from src.repositories.related_organisms_repository import RelatedOrganismsRepository


class BlastAPI:
    def __init__(self, database_url: str = "sqlite:///./database.db"):
        self.Entrez = Entrez
        self.NCBIWWW = NCBIWWW
        self.NCBIXML = NCBIXML
        self.logger = logging.getLogger(__name__)
        self.entrez_email = os.getenv("ENTREZ_EMAIL")
        
        # Database setup for caching
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def __get_16S_sequence(self, organism_name: str) -> tuple[str, str]:
        """
        Get 16S rRNA sequence and canonical organism name from NCBI.
        
        Returns:
            tuple: (fasta_sequence, canonical_organism_name)
        """
        search = self.Entrez.esearch(db="nucleotide", term=f"{organism_name}[Organism] AND 16S ribosomal RNA[Title]", retmax=1)
        record = self.Entrez.read(search)
        seq_id = record["IdList"][0]
        
        # Fetch the FASTA sequence
        fasta = self.Entrez.efetch(db="nucleotide", id=seq_id, rettype="fasta", retmode="text").read()
        
        # Fetch the GenBank record to get the canonical organism name
        gb_record = self.Entrez.efetch(db="nucleotide", id=seq_id, rettype="gb", retmode="text").read()
        
        # Extract the organism name from the GenBank record
        # Look for the ORGANISM line which contains the canonical name
        canonical_name = organism_name  # default fallback
        for line in gb_record.split('\n'):
            if line.strip().startswith('ORGANISM'):
                # Format: "  ORGANISM  Escherichia coli"
                canonical_name = line.split('ORGANISM')[1].strip()
                break
        
        self.logger.info(f"Canonical organism name from NCBI: {canonical_name}")
        return fasta, canonical_name

    def __run_blast(self, sequence: str, exclude_organism: str) -> str:
        """
        Run BLAST query excluding the target organism.
        
        Args:
            sequence: The 16S rRNA sequence to BLAST
            exclude_organism: Canonical organism name to exclude from results
        """
        result_handle = self.NCBIWWW.qblast(
            program="blastn",
            database="nt",
            sequence=sequence,
            entrez_query=f"NOT {exclude_organism}[Organism]",
            hitlist_size=25  # get many results so we can deduplicate
        )
        return result_handle

    def __parse_blast_results(self, result_handle: str) -> str:
        blast_record = next(self.NCBIXML.parse(result_handle))
        return blast_record

    def __filter_blast_results(self, blast_record: str, exclude_organism: str) -> str:
        """
        Filter BLAST results to get unique species, excluding the target organism.
        
        Args:
            blast_record: Parsed BLAST results
            exclude_organism: Canonical organism name to exclude (case-insensitive)
        """
        unique_species = {}
        exclude_organism_lower = exclude_organism.lower()
        
        for alignment in blast_record.alignments:
            title = alignment.hit_def
            hsp = alignment.hsps[0]
            identity = (hsp.identities / hsp.align_length) * 100
            score = hsp.score
            parts = title.split()
            if len(parts) >= 2:
                species_name = " ".join(parts[:2])
            else:
                continue
            
            # Skip if this is the target organism (case-insensitive) or already in results
            if species_name.lower() == exclude_organism_lower or species_name in unique_species:
                continue
            
            unique_species[species_name] = {
                "title": title,
                "score": score,
                "identity": identity,
                "align_length": hsp.align_length
            }
        return unique_species
    
    def __sort_blast_results(self, unique_species: dict) -> list:
        sorted_species = sorted(unique_species.items(), key=lambda x: x[1]["identity"], reverse=True)
        return [species for species, data in sorted_species]

    def __filter_species(self, unique_species: list) -> list:
        filtered_species = []
        for species in unique_species:
            if 'Uncultured' in species:
                continue
            if species.endswith('sp.'):
                continue
            if ' sp.' in species:
                continue
            filtered_species.append(species)
        return filtered_species

    def get_top_10_related_organisms(self, organism_name: str) -> list:
        """
        Get top 10 related organisms using BLAST analysis.
        
        Args:
            organism_name: Name of the target organism (can be informal like "E. coli")
            
        Returns:
            List of related organism names
        """
        # Check cache first
        session = self.SessionLocal()
        try:
            repository = RelatedOrganismsRepository(session)
            cached_entry = repository.get_by_organism(organism_name.lower())
            
            if cached_entry:
                self.logger.info(f"Cache hit for organism: {organism_name}")
                # Parse the comma-separated string back to a list
                related_organisms_list = [org.strip() for org in cached_entry.related_organisms.split(',')]
                return related_organisms_list
            
            self.logger.info(f"Cache miss for organism: {organism_name}. Running BLAST query...")
            
            # Cache miss - run the actual BLAST query
            # Get the 16S sequence AND the canonical organism name from NCBI
            sequence, canonical_name = self.__get_16S_sequence(organism_name)
            
            # Run BLAST excluding the canonical organism name
            result_handle = self.__run_blast(sequence, canonical_name)
            blast_record = self.__parse_blast_results(result_handle)
            
            # Filter results, excluding the canonical organism name
            unique_species = self.__filter_blast_results(blast_record, canonical_name)
            sorted_species = self.__sort_blast_results(unique_species)
            filtered_species = self.__filter_species(sorted_species)
            
            result = [species for species in filtered_species][:10] if len(filtered_species) > 10 else filtered_species
            
            # Cache the result
            if result:
                # Store as comma-separated string
                related_organisms_str = ','.join(result)
                repository.create(organism_name.lower().strip(), related_organisms_str)
                self.logger.info(f"Cached related organisms for: {organism_name}")
            
            return result
            
        finally:
            session.close()