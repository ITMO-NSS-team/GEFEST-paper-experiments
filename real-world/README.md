In this folder real-world cases and paper results are presented.

Each case is presented as an easy-to-run script. Everything that needs to be done
is to configurate prepared toolkits:

- __Domain__
***
    domain = configurate_domain(poly_num=opt.n_polys,
                                points_num=opt.n_points,
                                is_closed=opt.is_closed)

- __Sampler__
***
    sampler = configurate_sampler(domain=domain)

- __Estimator__
***
    estimator = configurate_estimator(domain=domain,
                                      path_to_model=opt.path_to_model)

- __Optimizer__
***
    optimizer = configurate_optimizer(pop_size=opt.pop_size,
                                      crossover_rate=opt.c_rate,
                                      mutation_rate=opt.m_rate,
                                      task_setup=task_setup)

After tools are configurated the design step should be called
***
    design(n_steps=opt.n_steps,
           pop_size=opt.pop_size,
           estimator=estimator,
           sampler=sampler,
           optimizer=optimizer,
           extra=False)
The results will be collected in folder _HistoryFiles_

For detailed settings of the tools, see https://github.com/quickjkee/GEFEST/tree/main/cases

__Note__:
 - Before run scripts install GEFEST 
***
    $ pip install --ignore-installed -r real-world/requirements.txt
- To run microfluidic case you should have COMSOL Multiphysics and MPh library
***
    $ pip install MPh