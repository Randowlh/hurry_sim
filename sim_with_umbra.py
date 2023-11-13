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

    for i in range(start_id,end_id-1):
        for j in range(0,total_num):
            edge_list.append([i*total_num+j+1,(i+1)*total_num+j+1,inf])

    for i in range(start_id,end_id):
        for j in range(0,num_satellite):
            if matching[i].get(j) is not None:
                edge_list.append([i*total_num+j+1,total_num*i+matching[i][j]+1,ground_station_max_transmit_packets_per_time_step[matching[i][j]-num_satellite]])


    for i in range(start_id,end_id):
        for j in range(0,num_groundstation):
            edge_list.append([i*total_num+num_satellite+j+1,end_node_id,ground_station_handle_packages_per_time_step[j]])
            
    return edge_list

def extract_data_from_flow(max_flow, num_timeslots, num_satellites, num_groundstations,total_sim_time_ns,sim_time_step_ns,epoch):
    end_node_id = num_timeslots * (num_satellites + num_groundstations) + 1
    routing_table = []
    time_slot=0
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        now=time_since_epoch*u.ns+epoch
        routing_table.append([now])
        for i in range(0,num_satellites):
            routing_table[time_slot].append([])
        time_slot+=1
    for arc in range(max_flow.NumArcs()):
        if max_flow.Flow(arc) > 0 and max_flow.Head(arc) != end_node_id and max_flow.Tail(arc) != 0 and max_flow.Head(arc)// (num_satellites + num_groundstations) == max_flow.Tail(arc)// (num_satellites + num_groundstations):
            sender = (max_flow.Tail(arc)-1) % (num_satellites + num_groundstations)
            receiver = (max_flow.Head(arc)-1) % (num_satellites + num_groundstations)
            time_slot= (max_flow.Tail(arc)-1) // (num_satellites + num_groundstations)
            try:
                routing_table[time_slot][sender+1].append([receiver, max_flow.Flow(arc)])
            except:
                print("time_slot",time_slot,"sender",sender,"receiver",receiver,"max_flow.Flow(arc)",max_flow.Flow(arc))
    return routing_table

    
def sim_with_umbra( total_sim_time_ns,
                    sim_time_step_ns,
                    satellites,
                    ground_stations,
                    # ground_station_flag,
                    epoch,
                    satellite_generated_packages_per_time_step,
                    ground_station_max_transmit_packets_per_time_step,#list 每个地面站星地链路大小
                    ground_station_handle_packages_per_time_step,#list地面站到数据中心带宽大小
                    max_gsl_length_m

                   ):
    
    throughput=[]
    matching=[]
    for time_since_epoch in range(0,total_sim_time_ns,sim_time_step_ns):
        print("Simulation progress: {:.2%}".format(time_since_epoch / total_sim_time_ns))
        now=time_since_epoch*u.ns+epoch
        G=nx.Graph()
        for i in range(0, len(satellites)):
            G.add_node(i, bipartite=0)
        for i in range(0,len(ground_stations)):
            G.add_node(i+len(satellites), bipartite=1)
        for i in range(0,len(satellites)):
            for j in range(0,len(ground_stations)):
                if(distant_tools.distance_m_ground_station_to_satellite(ground_stations[j],satellites[i],str(epoch),str(now))<=max_gsl_length_m):
                    # print("i",i,"j",j)
                    G.add_edge(i,j+len(satellites))
        uu = [n for n in G.nodes if G.nodes[n]['bipartite'] == 0]
        
        # 使用最大匹配算法求解最大匹配
        matching.append(nx.bipartite.maximum_matching(G, top_nodes=uu))
        # print(matching)

    flow_graph=construct_flow_graph(matching,0,len(matching),len(satellites),len(ground_stations),satellite_generated_packages_per_time_step,ground_station_max_transmit_packets_per_time_step,ground_station_handle_packages_per_time_step)
    end_node_id=len(matching)*(len(satellites)+len(ground_stations))+1
    max_flow = pywrapgraph.SimpleMaxFlow()
    for edge in flow_graph:
        max_flow.AddArcWithCapacity(edge[0], edge[1], edge[2])
    if max_flow.Solve(0, end_node_id) != max_flow.OPTIMAL:
        print('There was an issue with the max flow input.')
        exit()
    route_data = extract_data_from_flow(max_flow, len(matching), len(satellites), len(ground_stations),total_sim_time_ns,sim_time_step_ns,epoch)
    return route_data
    
   