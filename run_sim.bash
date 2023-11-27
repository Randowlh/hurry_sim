#Usage: python main.py [total_sim_time_ms] [sim_time_step_ms] [satellite_generated_packages_per_time_step] [ground_station_max_transmit_packets_per_time_step]
rm -f nohup.out
nohup python -u main.py 10000000 1000 10000 4 10 10 sim_heavy_100 &
nohup python -u main.py 10000000 1000 10000 4 100 100 sim_light_100 &

nohup python -u main.py 5000000 1000 10000 4 10 10 sim_heavy_100 &
nohup python -u main.py 5000000 1000 10000 4 100 100 sim_light_100 &

nohup python -u main.py 1000000 1000 10000 4 10 10 sim_heavy_100 &
nohup python -u main.py 1000000 1000 10000 4 100 100 sim_light_100 &

# nohup python -u main.py 400000 1000 20000 4 10 10 sim_heavy_100 &
# nohup python -u main.py 400000 1000 10000 4 100 100 sim_light_1000 &
# nohup python -u main.py 400000 1000 10000 4 10 10 sim_heavy_1000 &
# nohup python -u main.py 400000 1000 30000 4 100 100 sim_light_1000 &
# nohup python -u main.py 400000 1000 5000  10 10 sim_heavy_1000 &
# nohup python -u main.py 400000 1000 1000 100 100 sim_light_1000 &

# nohup python -u main.py 1600000 4000 20000  4 10 10 sim_heavy_1000 &
# nohup python -u main.py 1600000 4000 40000 4 100 100 sim_light_1000 &
# nohup python -u main.py 800000 2000 20000 4 10 10 sim_heavy_1000 &
# nohup python -u main.py 800000 2000 10000 4 100 100 sim_light_1000 &

