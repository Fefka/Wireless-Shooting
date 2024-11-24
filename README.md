# Cassini Hackathon 2024  
## Project: Wireless Shooting  

### Challenge  
**Unmanned drone applications for defence & security operations**  

### Problem to Solve  
In the rapidly evolving battlefield, drones have become a critical component of military operations. Controlling airspace, neutralizing enemy drones, and ensuring border security are among the most significant challenges in defence and security.  

---

## Project Idea  
**Wireless Shooting** is a defensive system based on **deauthentication attacks**, designed to neutralize enemy drones by disrupting their Wi-Fi connection. Our system utilizes three autonomous drones that collaboratively locate and track an enemy drone.  

### How It Works:  
1. **Coordinate Sharing:** Each drone transmits its coordinates via a serial interface.  
2. **Data Processing:** An external machine processes the coordinates, visualizes the drones' positions on a map (using the Matplotlib library), and calculates the enemy drone's location through a triangulation algorithm.  

---

## Project Functionality  

### **1. Deauthentication Attack**  
Three drones collaborate to disrupt the Wi-Fi connection of an enemy drone, causing it to lose control.  

### **2. Target Localization**  
- Each drone monitors the enemy drone’s position by simulating Wi-Fi signal ranges using circles with a 100 m radius.  

### **3. Triangulation Algorithm**  
- The enemy drone’s position is determined as the intersection of the signal range circles, enabling precise localization.  

### **4. Visualization**  
- Real-time data are displayed on a map, allowing operators to continuously monitor the situation.  

---

## Potential Applications  
- Neutralizing enemy drones in **military operations**.  
- Patrolling borders to prevent unauthorized drone activity in **restricted areas**.  
- Protecting critical infrastructure from unauthorized aerial devices.  

---

## Conclusion  
By leveraging drone collaboration and advanced triangulation algorithms, the **Wireless Shooting** project offers a cutting-edge approach to drone defence in modern operational environments.
