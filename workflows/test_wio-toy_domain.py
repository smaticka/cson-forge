import cson_forge
from datetime import datetime
import config
from roms_tools import VolumeRelease

model_name = "roms-marbl"
grid_name = "wio-toy"

start_time = datetime(2012, 1, 1)
end_time = datetime(2012, 1, 2)

boundaries={
        "south": True,
        "east": True,
        "north": True,
        "west": True, 
    }

np_eta = 5 # number of partitions in eta (y) 
np_xi = 2 # number of partitions in xi (x) 

grid_kwargs = dict(
    nx=20,           # number of grid points in x-direction
    ny=20,           # number of grid points in y-direction
    N=10,             # number of vertical layers
    size_x=8000,       # domain size in x-direction (km)
    size_y=8000,       # domain size in y-direction (km)
    center_lon=60.0,    # center longitude (E)
    center_lat=-4.0,    # center latitude (S)
    rot=0,            # no rotation
)

# cdr releases
vol1 = {"type":"VolumeRelease", 
        "name":"volume_1",
        "lat":60.0,  # degree N
        "lon":-4,  # degree E
        "depth":10,  # m
        "volume_fluxes":1000,  # m3/s
        "tracer_concentrations":{
            "temp": 20.0,  # degrees C
            "salt": 1.0,  # psu
            "ALK": 2000.0,  # meq/m3
            }
    }

vol2 = {"type":"VolumeRelease", 
        "name":"volume_2",
        "lat":60.5,  # degree N
        "lon":-3.9,  # degree E
        "depth":1,  # m
        "volume_fluxes":500,  # m3/s
        "tracer_concentrations":{
            "temp": 20.0,  # degrees C
            "salt": 1.0,  # psu
            "ALK": 2000.0,  # meq/m3
        }
    }

# instantiate the model object
ocn = cson_forge.OcnModel(
    model_name=model_name,
    grid_name=grid_name,
    grid_kwargs=grid_kwargs,
    boundaries=boundaries,    
    start_time=start_time,
    end_time=end_time,
    np_eta=np_eta,
    np_xi=np_xi,
    cdr_list=[vol1, vol2],
)

# ensure that the source data is present
ocn.prepare_source_data(clobber=False)


# assemble model input datasets — returns `inputs`, a list of ROMS Tools objects
inputs = ocn.generate_inputs(clobber=True)

# build the model
parameters = {
    "param.opt": dict(NP_XI=np_xi, NP_ETA=np_eta, NX=ocn.grid.nx, NY=ocn.grid.ny, NK=ocn.grid.N),
    "river_frc.opt": dict(nriv=inputs["rivers"].ds.sizes["nriver"]),
    "cdr_frc.opt": dict(CDR_SOURCE='.true.', CDR_FILE="'roms_cdr.nc'", NCDR=2, CDR_VOLUME='.true.'),
}

# run a simulate
ocn.build(parameters, clean=True)

ocn.run(case="test-case.001")
