# Setup
Install conda (OPTIONAL) and setup env
```
conda create -n overcooked
```

Now install requirements
```
pip install -r requirements.txt
```

# Run Setup

## Arduino IDE
1. Connect arduino and upload Arduino pulse sensor code
2. Connect sensors and calibrate signals for 3-5 mins
   
## Overcooked Game: Docker
1. Navigate to the project directory
```sh
cd overcooked-demo
```
2. Run the setup script
```sh
./up.sh
```
3. The game can be accessed from `localhost`

## Sensor Server
1. Change trial number in `sensor_read.py`. eg: `trial-1`
2. Run the sensor script in terminal
```bash
python sensor_read.py
```
3. The server is running on `localhost:5050`

## Experiment Data
The experiment data results are stored inside `overcooked-demo` directory for each trial. The data from our experiments can be seen in the folder `./data`.

## Analysis
To preprocess and analyse the dataset the jupyter notebook `final_code.ipynb` was utilized followed by which the processed results were loaded in JASP for further metrics and plotting found in folder `Jasp_code`.


# Code References
Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lespinasse, F., Pham, H., Schölzel, C., & Chen, S. H. A. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. Behavior Research Methods, 53, 1689-1696. https://doi.org/10.3758/s13428-020-01516-y

Overcooked Demo Code Utilized and modified from https://github.com/HumanCompatibleAI/overcooked-demo.