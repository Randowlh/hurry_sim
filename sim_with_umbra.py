import distant_tools
import networkx as nx
import astropy.units as u
from ortools.graph import pywrapgraph
def construct_flow_graph(matching,
                         start_id,
                         end_id,
                         num_satellite,
                         num_groundstation,
                         satellite_generated_packages_per_time_step,
                         ground_station_max_transmit_packets_per_time_step,
                         ground_station_handle_packages_per_time_step):
    inf = 9999999999 
    end_node_id=end_id*(num_satellite+num_groundstation)+1
    edge_list=[]
    total_num=num_satellite+num_groundstation
    for i in range(start_id,end_id):
        for j in range(0,num_satellite):
            edge_list.append([0,i*total_num+j+1,satellite_generated_packages_per_time_step])
            # print("satellite_generated_packages_per_time_step")
            # print([0,i*total_num+j+1,satellite_generated_packages_per_time_step])
    for i in range(start_id,end_id-1):
        for j in range(0,total_num):
            edge_list.append([i*total_num+j+1,(i+1)*total_num+j+1,inf])
            # print("time_edge")
            # print([i*total_num+j+1,(i+1)*total_num+j+1,inf])
    for i in range(start_id,end_id):
        for j in range(0,num_satellite):
            if matching[i].get(j) is not None:
                edge_list.append([i*total_num+j+1,total_num*i+matching[i][j]+1,ground_station_max_transmit_packets_per_time_step[matching[i][j]-num_satellite]])
                # print("satellite_to_groundstation")
                # print([i*total_num+j+1,total_num*i+matching[i][j]+1,ground_station_max_transmit_packets_per_time_step[matching[i][j]-num_satellite]])
    for i in range(start_id,end_id):
        for j in range(0,num_groundstation):
            edge_list.append([i*total_num+num_satellite+j+1,end_node_id,ground_station_handle_packages_per_time_step[j]])
            # print("groundstation_to_datacenter")
            # print([i*total_num+num_satellite+j+1,end_node_id,ground_station_handle_packages_per_time_step[j]])
    return edge_list

    
def sim_with_umbra( total_sim_time_ns,
                    sim_time_step_ns,
                    satellites,
                    ground_stations,
                    # ground_station_flag,
                    epoch,
                    satellite_generated_packages_per_time_step,
                    ground_station_max_transmit_packets_per_time_step,#list 每个地面站星地链路大小
                    ground_station_max_cap,#地面站队列大小
                    ground_station_handle_packages_per_time_step,#list地面站到数据中心带宽大小
                   ):
    
    throughput=[]
    matching=[]
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        print("Simulation progress: {:.2%}".format(time_since_epoch / total_sim_time_ns), end="\r")
        now=time_since_epoch*u.ns+epoch
        G=nx.Graph()
        for i in range(0, len(satellites)):
            G.add_node(i, bipartite=0)
        for i in range(0,len(ground_stations)):
            G.add_node(i+len(satellites), bipartite=1)
        for i in range(0,len(satellites)):
            for j in range(0,len(ground_stations)):
                if(distant_tools.distance_m_ground_station_to_satellite(ground_stations[j],satellites[i],str(epoch),str(now))):
                    G.add_edge(i,j+len(satellites))
        
        
        # 使用最大匹配算法求解最大匹配
        matching.append(nx.bipartite.maximum_matching(G))
        # print(matching)

    flow_graph=construct_flow_graph(matching,0,len(matching),len(satellites),len(ground_stations),satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step)
    end_node_id=len(matching)*(len(satellites)+len(ground_stations))+1
    max_flow = pywrapgraph.SimpleMaxFlow()
    for edge in flow_graph:
        max_flow.AddArcWithCapacity(edge[0], edge[1], edge[2])
    if max_flow.Solve(0, end_node_id) != max_flow.OPTIMAL:
        print('There was an issue with the max flow input.')
        exit()

    for i in range(len(matching)):
        throughput.append(0)
    # for i in range(0, max_flow.NumArcs()):
    #     if max_flow.Flow(i) > 0:
            
    #         print('From source ' + str(max_flow.Tail(i)) + ' to destination ' + str(max_flow.Head(i)) + ' with flow ' + str(max_flow.Flow(i)))
    for k in range(0, max_flow.NumArcs()):
        if max_flow.Head(k)==end_node_id and max_flow.Tail(k)%((len(satellites)+len(ground_stations)))>=len(satellites):
            throughput[max_flow.Tail(k)//(len(satellites)+len(ground_stations))]+=max_flow.Flow(k)
            
    return throughput
        
    # flow_edge={}
    # for i in range(0, max_flow.NumArcs()):
    #     if max_flow.Flow(i) > 0:
    #         print('From source ' + str(max_flow.Tail(i)) + ' to destination ' + str(max_flow.Head(i)) + ' with flow ' + str(max_flow.Flow(i)))
    #         if(max_flow.Tail(i)%((len(satellites)+len(ground_stations)))<len(satellites)):
    #             flow_edge[max_flow.Tail(i)]=[max_flow.Head(i),max_flow.Flow(i)]
    # current_time_step = 0
    # for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
    #     total_throughput=0
    #     for i in range(0, len(ground_stations)):
    #         ground_station_flag[i]=0
    #     print("Simulation progress: {:.2%}".format(time_since_epoch / total_sim_time_ns), end="\r")
    #     now=time_since_epoch*u.ns+epoch
        
    #     for sat_id in range(len(satellites)):
    #         satellite=satellites[sat_id]
    #         satellite_queue[sat_id]+=satellite_generated_packages_per_time_step
    #         target=flow_edge[sat_id+1+current_time_step*(len(satellite)+len(ground_stations))][0]-
            
            
            
            
    #         for j in range(len(ground_stations)):
    #             if flow_edge[i][0]==j+len(satellites):
    #                 satellite_queue-=flow_edge[i][1]
    #         m_satellite_queue[i]+=satellite_queue
    #         for j in range(len(ground_stations)):
    #             if flow_edge[i][0]==j+len(satellites):
    #                 m_ground_station_queue[j]+=flow_edge[i][1]