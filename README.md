Cassini Hackathon 2024 
Project: Wireless Shooting 
 
Challenge: Unmanned drone applications for defence & security operations 
 
Problem to Solve: 
In the rapidly evolving battlefield, drones have become a critical component of military operations. Controlling airspace, neutralizing enemy drones, and ensuring border security are among the most significant challenges in defence and security. 
 
Project Idea: 
Wireless Shooting is a defensive system based on deauthentication attacks, designed to neutralize enemy drones by disrupting their Wi-Fi connection. Our team has developed a system involving three autonomous drones that collaboratively locate and track an enemy drone. Each drone transmits its coordinates via a serial interface. These data are processed by an external machine that visualizes their positions on a map using the Matplotlib library and calculates the location of the enemy drone through a triangulation algorithm. 
 
Project Functionality: 
Deauthentication Attack: Three drones work together to disrupt the Wi-Fi connection of the enemy drone, causing it to lose control. 
Target Localization: Each drone monitors the enemy drone’s position by forming circles with a 100 m radius, simulating the Wi-Fi signal range. 
Triangulation Algorithm: The enemy drone's position is calculated as the intersection of the signal range circles, enabling precise target localization. 
Visualization: The data are displayed on a real-time map, allowing the operator to monitor the situation continuously. 
 
Potential Applications: 
Military operations to neutralize enemy drones. 
Patrolling borders and preventing unauthorized drone activity in restricted areas. 
Protection of critical infrastructure from unauthorized aerial devices. 
 
By leveraging drone collaboration and advanced triangulation algorithms, the Wireless Shooting project showcases a modern approach to drone defence in operational environments. 
