import traci
import os
import sys


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = 'sumo-gui'
traci.start([sumoBinary, "-c", "sumo_config.sumocfg"]) #Restart Kernel if you get an error here

total_waiting_time = {}
vehicle_count = {}
vehicle_current_edge = {}  # Track each vehicle's current edge

# main loop. do something every simulation step until no more vehicles are
# loaded or running
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    # Update vehicle positions and count entries per edge
    for veh_id in traci.vehicle.getIDList():
        current_edge = traci.vehicle.getRoadID(veh_id)
        previous_edge = vehicle_current_edge.get(veh_id, None) #return None if no edge found

        if current_edge != previous_edge:
            #Vehicle enter new edge
            if current_edge not in vehicle_count:
                vehicle_count[current_edge] = 0
            vehicle_count[current_edge] += 1
            vehicle_current_edge[veh_id] = current_edge # set previous edge = current edge

    #Calculate waiting time for each edge
    for edge_id in traci.edge.getIDList():
        waiting_time = traci.edge.getWaitingTime(edge_id)
        if edge_id not in total_waiting_time:
            total_waiting_time[edge_id] = 0
        total_waiting_time[edge_id] += waiting_time

# end simulation
sys.stdout.flush()
traci.close()
print(vehicle_count.items())
# #Calculate avg waiting time on each edge
average_waiting_time = {}
print("Total waiting time per edge:")
for edge, time in total_waiting_time.items():
    if edge in ['E0','E1', '-E2', 'E3']: #Only this edge have traffic flow on it
        print(f"{edge}: {time}s")
        count = vehicle_count[edge]
        if count > 0:
            average_waiting_time[edge] = total_waiting_time[edge] / count
        else:
            average_waiting_time[edge] = 0

#Print result
print("Average waiting time per edge:")
for edge in average_waiting_time:
    print(f"{edge}: {round(average_waiting_time[edge],2)} s")