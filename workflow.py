
import os
from gwf import Workflow, AnonymousTarget
from gwf.workflow import collect

gwf = Workflow(defaults={'account': 'baboons'})

vcf_file_name = ''
chromosome = '7'
samples = []
population = 'some_population'
dedicated_indiv_list =['XXXXX', 'XXXXX', 'XXXXX', 'XXXXX']
mutation_rate = 1.247e-08
generation_time = 29

smc_file_name_list = []
for dedicated_indiv in dedicated_indiv_list:

    smc_file_name = f'steps/smcpp/{dedicated_indiv}_{max_missing}.txt'
    smc_file_name_list.append(smc_file_name)

    gwf.target(name=f'vcf2smc_{dedicated_indiv.replace("-", "_")}',
        inputs=[vcf_file_name], 
        outputs=[smc_file_name], 
        walltime='3-00:00:00', 
        memory='8g') << f"""

    mkdir -p steps/smcpp
    singularity run docker://terhorst/smcpp:latest vcf2smc \
         --cores 4 -d {dedicated_indiv} {dedicated_indiv} \
         --missing-cutoff 50000 \
        {vcf_file_name} {smc_file_name} {chromosome} {population}:{','.join(samples)}
    """

gwf.target(name='estimate',
     inputs=smc_file_name_list, 
     outputs=[], 
     cores=4,
     walltime='4-00:00:00', 
     memory='16g') << f"""

singularity run docker://terhorst/smcpp:latest estimate \
    -o {chromosome} --cores 4 --timepoints 35 4e4 --spline pchip {mutation_rate} {' '.join(smc_file_name_list)}
"""

gwf.target(name='plot',
     inputs=['model.final.json'], 
     outputs=['plot.png'], 
     walltime='4-00:00:00', 
     memory='16g'
     ) << f"""

singularity run docker://terhorst/smcpp:latest plot \
    -g {generation_time} -c plot.png model.final.json
"""



# demography_chr7 = scipy.interpolate.PchipInterpolator(generations_chr7, Ne_chr7, extrapolate=True)
# demography_chrX = scipy.interpolate.PchipInterpolator(generations_chrX, Ne_chrX, extrapolate=True)

# plt.plot(generations_chr7, [demography_chrX(g) / demography_chr7(g) for g in generations_chr7])

