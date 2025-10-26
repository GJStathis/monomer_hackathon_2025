


from Bio import Entrez
from Bio.Blast import NCBIWWW, NCBIXML

Entrez.email = "jamesgueguen@yahoo.fr"  # Required by NCBI

organism_name = "E.coli"

# Step 1: Get a representative 16S rRNA sequence for E. coli
print(f"Fetching 16S rRNA sequence for {organism_name}...")
search = Entrez.esearch(db="nucleotide", term=f"{organism_name}[Organism] AND 16S ribosomal RNA[Title]", retmax=1)
record = Entrez.read(search)
seq_id = record["IdList"][0]

fasta = Entrez.efetch(db="nucleotide", id=seq_id, rettype="fasta", retmode="text").read()

# Step 2: Run BLAST against nt database, excluding E. coli
print("Running BLAST (excluding Escherichia coli)...")
result_handle = NCBIWWW.qblast(
    program="blastn",
    database="nt",
    sequence=fasta,
    entrez_query="NOT Escherichia coli[Organism]",
    hitlist_size=100  # get many results so we can deduplicate
)

# Step 3: Parse BLAST results
blast_record = next(NCBIXML.parse(result_handle))

unique_species = {}
for alignment in blast_record.alignments:
    title = alignment.hit_def
    hsp = alignment.hsps[0]
    identity = (hsp.identities / hsp.align_length) * 100
    score = hsp.score

    # Extract species name (usually first two words of the title)
    parts = title.split()
    if len(parts) >= 2:
        species_name = " ".join(parts[:2])
    else:
        continue

    # Skip if it's E. coli or already recorded
    if "Escherichia coli" in species_name or species_name in unique_species:
        continue

    # Keep best (highest score) alignment per unique species
    unique_species[species_name] = {
        "title": title,
        "score": score,
        "identity": identity,
        "align_length": hsp.align_length
    }

# Step 4: Sort by similarity (descending)
sorted_species = sorted(unique_species.items(), key=lambda x: x[1]["identity"], reverse=True)

print("\nTop genetically related distinct species (excluding E. coli):\n")
for species, data in sorted_species[:10]:
    print(f"{species}\n  Identity: {data['identity']:.2f}% | Score: {data['score']} | Length: {data['align_length']}\n")

# Filter out 'Uncultured bacterium' and entries with 'sp.'
filtered_species = {}
for species, data in unique_species.items():
    # Skip if it contains 'Uncultured' (includes 'Uncultured bacterium', 'Uncultured prokaryote', etc.)
    if 'Uncultured' in species:
        continue
    # Skip if it ends with 'sp.' (e.g., "Shigella sp.", "Escherichia sp.")
    if species.endswith('sp.'):
        continue
    # Skip if it contains ' sp.'
    if ' sp.' in species:
        continue
    # Keep the rest
    filtered_species[species] = data

# Sort by similarity (descending)
sorted_filtered = sorted(filtered_species.items(), key=lambda x: x[1]["identity"], reverse=True)

print(f"Original species count: {len(unique_species)}")
print(f"Filtered species count: {len(filtered_species)}")
print(f"\nTop genetically related distinct species (filtered):\n")
for species, data in sorted_filtered[:10]:
    print(f"{species}\n  Identity: {data['identity']:.2f}% | Score: {data['score']} | Length: {data['align_length']}\n")

# Create a list with the names of the 10 highest related organisms
top_10_organisms = [species for species, data in sorted_filtered[:10]]
print(f"\nTop 10 related organisms list: {top_10_organisms}")
