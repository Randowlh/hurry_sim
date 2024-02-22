import distant_tools
import networkx as nx
import astropy.units as u
from ortools.graph import pywrapgraph
# import visiable_helper
import distant_tools
def construct_flow_graph(matching, start_id, end_id, num_satellite, num_groundstation, satellite_generated_packages_per_time_step, ground_station_max_transmit_packets_per_time_step, ground_station_handle_packages_per_time_step, edges, isl_max_cap,end_generate_id,current_queue_length):
    inf = 9999999999
    G = nx.DiGraph()
    end_node_id = end_id * (num_satellite + num_groundstation) + 1
    print("len current queue",len(current_queue_length))
    G.add_node(0)
    for i in range(0,num_satellite+num_groundstation):
        G.add_edge(0,(num_satellite + num_groundstation)*start_id+i+1,capacity=current_queue_length[i],weight=0)
        # print("fall back node",i+1,"capacity",current_queue_length[i],"id",(num_satellite + num_groundstation)*start_id+i+1)
    # 添加节点和边
    for i in range(start_id, end_generate_id):
        for j in range(0, num_satellite):
            G.add_edge(0, i * (num_satellite + num_groundstation) + j + 1, capacity=satellite_generated_packages_per_time_step, weight=0)
            

    for i in range(start_id, end_id - 1):
        for j in range(0, num_satellite + num_groundstation):
            G.add_edge(i * (num_satellite + num_groundstation) + j + 1, (i + 1) * (num_satellite + num_groundstation) + j + 1, capacity=inf, weight=1)

    for i in range(start_id, end_id - 1):
        for j in range(0, num_satellite):
            try:
                if matching[i].get(j) is not None:
                    G.add_edge(i * (num_satellite + num_groundstation) + j + 1, (i + 1) * (num_satellite + num_groundstation) + matching[i][j] + 1, capacity=ground_station_max_transmit_packets_per_time_step[matching[i][j] - num_satellite], weight=1)
            except:
                print("i=",i,"j=",j)
    for i in range(start_id, end_id):
        for j in range(0, num_groundstation):
            G.add_edge(i * (num_satellite + num_groundstation) + num_satellite + j + 1, end_node_id, capacity=ground_station_handle_packages_per_time_step[j], weight=0)

    for i in range(start_id, end_id - 1):
        for edge in edges:
            G.add_edge(i * (num_satellite + num_groundstation) + edge[0] + 1, (i + 1) * (num_satellite + num_groundstation) + edge[1] + 1, capacity=isl_max_cap, weight=1)
            G.add_edge(i * (num_satellite + num_groundstation) + edge[1] + 1, (i + 1) * (num_satellite + num_groundstation) + edge[0] + 1, capacity=isl_max_cap, weight=1)

    return G, end_node_id


def extract_data_from_flow(flow_dict, num_timeslots, num_satellites, num_groundstations, start_id,end_id, sim_time_step_ns, epoch):
    end_node_id =  end_id * (num_satellites + num_groundstations) + 1
    routing_table = []

    # 初始化路由表
    time_slot = 0
    for time_since_epoch in range(0, end_id):
        now = time_since_epoch * u.ns + epoch
        routing_table.append([now])
        for i in range(0, num_satellites):
            routing_table[time_slot].append([])
        time_slot += 1

    # 遍历所有的流量
    for from_node, to_dict in flow_dict.items():
        for to_node, flow in to_dict.items():
            if flow > 0 and to_node != end_node_id and from_node != 0:
                # print("sender",from_node,"receiver",to_node)
                sender = (from_node - 1) % (num_satellites + num_groundstations)
                receiver = (to_node - 1) % (num_satellites + num_groundstations)
                time_slot = (from_node - 1) // (num_satellites + num_groundstations)
                if sender != receiver:
                    try:
                        routing_table[time_slot][sender + 1].append([receiver, flow])
                    except Exception as e:
                        print(f"Error at time_slot {time_slot}, sender {sender}, receiver {receiver}, flow {flow}: {e}")

    return routing_table

def extract_queue_len_from_flow(flow_dict, num_timeslots, num_satellites, num_groundstations, start_id,end_id, sim_time_step_ns, epoch):
    end_node_id =end_id * (num_satellites + num_groundstations) + 1
    queue_len = []
    
    time_slot = 0
    for time_since_epoch in range(0, end_id):
        now = time_since_epoch * u.ns + epoch
        queue_len.append([])
        for i in range(0, num_satellites+num_groundstations):
            queue_len[time_slot].append(0)
        time_slot += 1
        
    #遍历 flow_dict
    for from_node, to_dict in flow_dict.items():
        for to_node, flow in to_dict.items():
            if flow > 0 and to_node != end_node_id:
                sender = (from_node ) % (num_satellites + num_groundstations)
                receiver = (to_node - 1) % (num_satellites + num_groundstations)
                time_slot = (to_node - 1) // (num_satellites + num_groundstations)
                try:
                    # print("send=",sender,receiver,flow)
                    queue_len[time_slot][receiver] += flow
                    # print("queue len added!")
                except Exception as e:
                    print(f"Error!!!! at time_slot {time_slot}, sender {sender}, receiver {receiver}, flow {flow}: {e}")
    return queue_len


def sat_choose(visiable_helper,gid,now,sat_choosed,num_satellite):
    max_server_time=visiable_helper.epoch
    max_server_id=-1 
    for sid in range(num_satellite):
        if(not(sid in sat_choosed)):
            if(visiable_helper.visible_times[gid][sid][0]<=now and visiable_helper.visible_times[gid][sid][1]>=now):
                if(visiable_helper.visible_times[gid][sid][1]>max_server_time):
                    max_server_time=visiable_helper.visible_times[gid][sid][1]
                    max_server_id=sid
    return max_server_id

    
def sim_with_hurry( total_sim_time_ns,
                    sim_time_step_ns,
                    satellites,
                    ground_stations,
                    # ground_station_flag,
                    epoch,
                    satellite_generated_packages_per_time_step,
                    ground_station_max_transmit_packets_per_time_step,#list 每个地面站星地链路大小
                    ground_station_handle_packages_per_time_step,#list地面站到数据中心带宽大小
                    max_gsl_length_m,
                    edges,
                    isl_max_cap,
                    total_generate_time_ns,
                    current_loop_id,
                    current_queue_length,
                    generate_length
                   ):
    
    
    throughput=[]
    matching=[]
    
    # vhp=visiable_helper.Visible_time_helper(ground_stations,satellites,max_gsl_length_m,epoch,sim_time_step_ns,total_sim_time_ns)
    sat_choose_gs_pre=[]
    total_sim_time_ns=min(total_sim_time_ns,(generate_length+current_loop_id)*sim_time_step_ns)
    print("total_generate_time_ns=",total_generate_time_ns)
    match={}
    for time_since_epoch in range(current_loop_id*sim_time_step_ns,total_sim_time_ns,sim_time_step_ns):
        print("cost flow generating progress: {:.2%}".format(time_since_epoch / total_sim_time_ns))
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
        match=nx.bipartite.maximum_matching(G, top_nodes=uu)
        # 使用最大匹配算法求解最大匹配
        break;
    print("len match=",len(match))
    for i in range(0,len(ground_stations)):
        sat_choose_gs_pre.append(match[i+len(satellites)])
    
    G_sat = nx.Graph()
    # add node to the graph
    for i in range(0, len(satellites)):
        G_sat.add_node(i)
    # edges : [[1,2],[3,4]] : 1-2, 3-4
    for edge in edges:
        G_sat.add_edge(edge[0], edge[1])
        G_sat.add_edge(edge[1], edge[0]) #need correct
    
    for i in range(current_loop_id-1):
        matching.append(0)
    for time_since_epoch in range(current_loop_id*sim_time_step_ns,total_sim_time_ns,sim_time_step_ns):
        print("hurry generating progress: {:.2%}".format(time_since_epoch / total_sim_time_ns))
        now=time_since_epoch*u.ns+epoch
        sat_choose_cur={}
        # sat_choosed=[]
        for gid in range(len(ground_stations)):
            if(distant_tools.distance_m_ground_station_to_satellite(ground_stations[gid],satellites[sat_choose_gs_pre[gid]],str(epoch),str(now))<=max_gsl_length_m):
                sat_choose_cur[gid+len(satellites)]=sat_choose_gs_pre[gid]
                sat_choose_cur[sat_choose_gs_pre[gid]]=gid+len(satellites)
            else:
                for i in G_sat.neighbors(sat_choose_gs_pre[gid]):
                    if(distant_tools.distance_m_ground_station_to_satellite(ground_stations[gid],satellites[i],str(epoch),str(now))<=max_gsl_length_m):
                        sat_choose_cur[gid+len(satellites)]=i
                        sat_choose_cur[i]=gid+len(satellites)
                        break
            # sat_choosed.append(sat_choose_cur[gid+len(satellites)])
        # print(sat_choose_cur)
        for key in sat_choose_cur:
            sat_choose_cur[sat_choose_cur[key]]=key
        matching.append(sat_choose_cur)
        # print(matching)

    flow_graph, end_node_id = construct_flow_graph(matching, current_loop_id, current_loop_id+generate_length, len(satellites), len(ground_stations), satellite_generated_packages_per_time_step, ground_station_max_transmit_packets_per_time_step, ground_station_handle_packages_per_time_step, edges, isl_max_cap,total_generate_time_ns//sim_time_step_ns,current_queue_length)

    # 计算最小费用流
    flow_dict = nx.max_flow_min_cost(flow_graph, 0, end_node_id)

    route_data = extract_data_from_flow(flow_dict, len(matching), len(satellites), len(ground_stations), current_loop_id, current_loop_id+generate_length, sim_time_step_ns, epoch)
    queue_len = extract_queue_len_from_flow(flow_dict, len(matching), len(satellites), len(ground_stations),current_loop_id,  current_loop_id+generate_length, sim_time_step_ns, epoch)
    return route_data, queue_len
    
