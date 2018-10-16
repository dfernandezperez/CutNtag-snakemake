# Usage --> ./ChIPseq_pipeline.sh  <rules> (can be nothing or a rule defined in the snakefile without wildcards in the input files)     (the samples.json file must be created first, also remember to check the cluster and config files to put everything to your needs
rules=$1
snakemake --unlock
mkdir clusterLogs # Create folder to store the cluster output and error files
nohup snakemake $rules -j 999 --cluster-config cluster.json --latency-wait 120 --use-singularity --singularity-args "--bind /hpcnfs" \
--cluster "qsub -M {cluster.email} -m {cluster.EmailNotice} -N {cluster.jname} \
-l select=1:ncpus={cluster.cpu} -o {cluster.output} -e {cluster.error}" &>> snakemake.log&
