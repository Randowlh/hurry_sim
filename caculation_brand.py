import math
import distant_tools
def calculate_rate(initial_rate,satellite,ground_station,epoch,time):
    return initial_rate
    return rate

    distance=1000*distant_tools.distance_m_ground_station_to_satellite(ground_station,satellite,str(epoch),str(time))/1000
    # Constants (可以根据实际需要进行调整)
    height=780000
    max_gsl_length_m = 1260000.0000000000
    dis=math.sqrt(distance**2+height**2)
    max_dis=math.sqrt(max_gsl_length_m**2+height**2)
    # min band=0.4*initial_rate
    # max band=1*initial_rate
    # print("distance",distance)
    # print("dis",dis)
    # print("max_dis",max_dis)
    # print("initial_rate",initial_rate)
    # print("rate",initial_rate * (1 - 1*((dis**2) / (max_dis**2))))
    # print("precent",(1 - 1*((dis**2) / (max_dis**2))))
    # Calculate rate using parabolic algorithm
    rate = initial_rate * (1 - 0.3*((dis**2) / (max_dis**2)))
    
    return rate
    
    
    