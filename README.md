# topiary-examples

Jupyter notebooks demonstrating the [topiary](https://github.com/harmslab/topiary) ancestral sequence reconstruction package

[Topiary documentation](https://topiary-asr.readthedocs.io)

To download all demonstration notebooks and data you can clone this repository
with git or select `Code -> Download ZIP` above. 

## Demonstration notebooks

Click the colab link to run the notebook in google colab. Alternatively, you can
download the notebooks with the link and run them on a local computer. Running
the notebooks requires you to [install topiary](https://topiary-asr.readthedocs.io/en/latest/installation.html)
on your local computer. 

### Seed to alignment

This notebook walks through how to make a seed dataset for use in a topiary
analysis, then demonstrates the `seed_to_alignment` pipeline that
takes a seed dataset with a handful of sequences and generates a large multiple
sequence alignment. 

[Jupyter notebook](https://github.com/harmslab/topiary-examples/blob/main/notebooks/01_seed_to_alignment.ipynb) - <a href="https://githubtocolab.com/harmslab/topiary-examples/blob/main/notebooks/01_seed_to_alignment.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

### Alignment to ancestors

This notebook shows how to go from a topiary alignment to ancestral sequences. 
It demonstrates the `alignment_to_ancestors` pipeline, which identifies
the maximum likelihood phylogenetic model, generates a maximum likelihood gene
tree, reconciles the gene and species trees (if appropriate), and generates 
ancestral sequences. It also demonstrates the `bootstrap_reconcile` function, 
which generates bootstrap supports on the reconciled gene/species tree. 

[Jupyter notebook](https://github.com/harmslab/topiary-examples/blob/main/notebooks/03_alignment_to_ancestors.ipynb) - <a href="https://githubtocolab.com/harmslab/topiary-examples/blob/main/notebooks/03_alignment_to_ancestors.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
