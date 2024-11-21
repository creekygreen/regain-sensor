import pandas as pd
import numpy as np
import joblib
import time
import math
from mpu6050 import mpu6050


# Loads the model using joblib
def load_model(file_name):
    model = joblib.load(open(file_name, 'rb'))
    return model
    
# Classifies gait phase based on sensor data using random forest model
def get_gait_phase(model, thigh, shin, knee): 
    array = np.array([thigh, shin, knee])                                                # Create numpy array out of sensor data# 
    features = pd.DataFrame(array, columns=['Thigh Angle', 'Shin Angle', 'Knee Angle'])  # Convert numpy array to pandas dataframe
    gait_phase = rf_model.predict(features)                                              # Classify gait phase based on features using the random forest model
    return gait_phase

# get roll and pitch angles from accelorometer data
def get_roll_pitch(x, y, z): 
    roll = math.atan2(y, z) * 180 / math.pi                          # X-axis rotation
    pitch = math.atan2(-x, math.sqrt(y**2 + z**2)) * 180 / math.pi   # Y-axis rotation
    return roll, pitch

# xcale factor for MPU6050 gyroscope (depends on sensitivity setting)
def scale_gyro(coordinate): 
    gyro_scale = 131.0
    deg = coordinate / gyro_scale
    return deg

# get gyro data and convert to angular velocity in degrees per second
def get_gyro(gyro):
    x, y, z = gyro['x'], gyro['y'], gyro['z']   # Extract gyroscope data from dictionary
    x_deg = scale_gyro(x)
    y_deg = scale_gyro(y)
    z_deg = scale_gyro(z)
    return x_deg, y_deg, z_deg

def get_accel(accel):
    x, y, z = accel['x'], accel['y'], accel['z']
    return x, y, z

# moving average filter function
def moving_average(data):
    window_size = 5              # Moving average window size
    if len(data) >= window_size:
        return sum(data[-window_size:]) / window_size
    return sum(data) / len(data)

# Setup for two MPU6050 sensors
sensor_thigh = mpu6050(0x68)     # Thigh sensor address
sensor_shin = mpu6050(0x69)      # Shin sensor address (assuming different I2C address)

# Buffer for moving average filter (e.g., last 5 measurements)
accel_buffer_thigh = []
accel_buffer_shin = []

# Global variables for get_sensor_data()
previous_pitch_thigh = 0
previous_pitch_shin = 0
time_prev = time.time()

def get_knee_data():
    global previous_pitch_thigh, previous_pitch_shin, time_prev
    
    # Get thigh data from sensors
    accel_data_thigh = sensor_thigh.get_accel_data()
    gyro_data_thigh = sensor_thigh.get_gyro_data()
    
    # Get shin data from sensors
    accel_data_shin = sensor_shin.get_accel_data()
    gyro_data_shin = sensor_shin.get_gyro_data()
    
    # Get xyz coordinates from accelorometer data
    accel_x_thigh, accel_y_thigh, accel_z_thigh = get_accel(accel_data_thigh)
    accel_x_shin, accel_y_shin, accel_z_shin = get_accel(accel_data_shin)
    
    # Get xyz coordinates from gyroscope data
    gyro_x_thigh, gyro_y_thigh, gyro_z_thigh = get_gyro(gyro_data_thigh)
    gyro_x_shin, gyro_y_shin, gyro_z_shin = get_gyro(gyro_data_shin)
    
    # Calculate pitch angles
    _, pitch_thigh_accel = get_roll_pitch(accel_x_thigh, accel_y_thigh, accel_z_thigh)
    _, pitch_shin_accel = get_roll_pitch(accel_x_shin, accel_y_shin, accel_z_shin)

    # Add accelerometer values to buffer for moving average
    accel_buffer_thigh.append(pitch_thigh_accel)
    accel_buffer_shin.append(pitch_shin_accel)

    # Apply moving average filter to accelorometer data
    pitch_thigh_accel = moving_average(accel_buffer_thigh)
    pitch_shin_accel = moving_average(accel_buffer_shin)
    
    # Time difference between measurements
    time_now = time.time()
    dt = time_now - time_prev
    time_prev = time_now
    
    """
    Apply complementary filter to thigh and shin pitch angles.
    Adjust alpha dynamically based on movement (smaller alpha when stationary)
    """
    alpha = 0.98                                            # Initial complementary filter Value (changes depending on situation)
    if abs(gyro_y_thigh) < 1.0 and abs(gyro_y_shin) < 1.0:  # If nearly stationary
        alpha = 0.98                                        # More accelerometer influence
    else:
        alpha = 0.9                                         # More gyroscope influence when moving
    
    pitch_thigh = alpha * (previous_pitch_thigh + gyro_y_thigh * dt) + (1 - alpha) * pitch_thigh_accel
    pitch_shin = alpha * (previous_pitch_shin + gyro_y_shin * dt) + (1 - alpha) * pitch_shin_accel
    
    previous_pitch_thigh, previous_pitch_shin = pitch_thigh, pitch_shin    # Update previous pitch for the next iteration
    knee_angle = abs(pitch_thigh - pitch_shin)                             # Calculate knee angle (difference in pitch)
    
    # Round off values to whole numbers
    pitch_thigh = round(pitch_thigh)
    pitch_shin = round(pitch_shin)
    knee_angle = round(knee_angle)
    
    
    model = load_model()
    gait_phase = get_gait_phase(model, pitch_thigh, pitch_shin, knee_angle)

    return {  
        "pitch_thigh": pitch_thigh,
        "pitch_shin": pitch_shin,
        "knee_angle": knee_angle,
        "gait_phase": gait_phase
    }
