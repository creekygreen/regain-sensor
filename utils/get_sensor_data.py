# Imports
import smbus
import time
import math
from mpu6050 import mpu6050

# Setup for two MPU6050 sensors
sensor_thigh = mpu6050(0x68)  # Thigh sensor address
sensor_shin = mpu6050(0x69)   # Shin sensor address (assuming different I2C address)

# Complementary filter constant
alpha = 0.98  # Initial alpha value (for dynamic adjustment later)

# Buffer for moving average filter (e.g., last 5 measurements)
accel_buffer_thigh = []
accel_buffer_shin = []
window_size = 5  # Size of the moving average window

# Ccalculate roll and pitch angles using accelerometer data
def get_angles(accel_x, accel_y, accel_z):
    roll = math.atan2(accel_y, accel_z) * 180 / math.pi # Roll angle (X-axis rotation) 
    pitch = math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)) * 180 / math.pi # Pitch angle (Y-axis rotation)

    return roll, pitch

# Get gyro data and convert to angular velocity in degrees per second
def get_gyro_data(gyro_data):

    # Extract gyroscope data from dictionary
    gyro_x = gyro_data['x']
    gyro_y = gyro_data['y']
    gyro_z = gyro_data['z']
    
    # Scale factor for MPU6050 gyroscope (depends on sensitivity setting)
    gyro_scale = 131.0 
    gyro_x_deg = gyro_x / gyro_scale
    gyro_y_deg = gyro_y / gyro_scale
    gyro_z_deg = gyro_z / gyro_scale

    return gyro_x_deg, gyro_y_deg, gyro_z_deg

# Moving average filter function
def moving_average(data, window_size):
    if len(data) >= window_size:
        return sum(data[-window_size:]) / window_size
    return sum(data) / len(data)

# Round off values to nearest whole number
def round_off(value):
    return round(value) 

# Main loop
previous_pitch_thigh = 0
previous_pitch_shin = 0
time_prev = time.time()

while True:
    # Get accelerometer and gyroscope data from both sensors
    accel_data_thigh = sensor_thigh.get_accel_data()
    gyro_data_thigh = sensor_thigh.get_gyro_data()
    
    accel_data_shin = sensor_shin.get_accel_data()
    gyro_data_shin = sensor_shin.get_gyro_data()

    accel_x_thigh = accel_data_thigh['x']
    accel_y_thigh = accel_data_thigh['y']
    accel_z_thigh = accel_data_thigh['z']
    
    gyro_x_thigh, gyro_y_thigh, gyro_z_thigh = get_gyro_data(gyro_data_thigh)
    
    accel_x_shin = accel_data_shin['x']
    accel_y_shin = accel_data_shin['y']
    accel_z_shin = accel_data_shin['z']
    
    gyro_x_shin, gyro_y_shin, gyro_z_shin = get_gyro_data(gyro_data_shin)
    
    # Get pitch angles from accelerometer data
    _, pitch_thigh_accel = get_angles(accel_x_thigh, accel_y_thigh, accel_z_thigh)
    _, pitch_shin_accel = get_angles(accel_x_shin, accel_y_shin, accel_z_shin)

    # Add accelerometer values to buffer for moving average
    accel_buffer_thigh.append(pitch_thigh_accel)
    accel_buffer_shin.append(pitch_shin_accel)

    # Apply moving average filter to accelerometer data
    pitch_thigh_accel = moving_average(accel_buffer_thigh, window_size)
    pitch_shin_accel = moving_average(accel_buffer_shin, window_size)

    # Time difference between measurements
    time_now = time.time()
    dt = time_now - time_prev
    time_prev = time_now
    
    # Apply complementary filter for thigh and shin pitch angles
    # Adjust alpha dynamically based on movement (smaller alpha when stationary)
    if abs(gyro_y_thigh) < 1.0 and abs(gyro_y_shin) < 1.0:  # If nearly stationary
        alpha = 0.98  # More accelerometer influence
    else:
        alpha = 0.9   # More gyroscope influence when moving
    
    pitch_thigh = alpha * (previous_pitch_thigh + gyro_y_thigh * dt) + (1 - alpha) * pitch_thigh_accel
    pitch_shin = alpha * (previous_pitch_shin + gyro_y_shin * dt) + (1 - alpha) * pitch_shin_accel
    
    # Update previous pitch for the next iteration
    previous_pitch_thigh = pitch_thigh
    previous_pitch_shin = pitch_shin
    
    # Calculate knee angle (difference in pitch)
    knee_angle = abs(pitch_thigh - pitch_shin)
    
    # Round off values to whole numbers
    pitch_thigh = round_off(pitch_thigh)
    pitch_shin = round_off(pitch_shin)
    knee_angle = round_off(knee_angle)
    
    # Print the filtered and rounded angles (whole numbers)
    print(f"Filtered Thigh Angle: {pitch_thigh}°")
    print(f"Filtered Shin Angle: {pitch_shin}°")
    print(f"Knee Angle: {knee_angle}°")
    
    time.sleep(0.1)
