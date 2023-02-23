from machine import Pin
import network
import socket
from machine import I2C
import ssd1306
from machine import RTC
import utime
import ujson, urequests


def read(addr):
    cs(0)
    res = bytearray(2)
    hspi.readinto(res, 128|addr)
    cs(1)
    return res[1]

hspi = machine.SPI(1,baudrate = 1500000, polarity = 1, phase = 1)
cs = machine.Pin(2, machine.Pin.OUT, value = 1)
cs(0)
#hspi.write(b'\x31\x0c')
hspi.write(b'\x31\x0d')
cs(1)

cs(0)
hspi.write(b'\x2d\x08')
cs(1)  

cs(0)
hspi.write(b'\x2c\x0a')
cs(1)

cs(0)
hspi.write(b'\x2e\x00')
cs(1)

cs(0)
hspi.write(b'\x38\x00')
cs(1)

#i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))
#display = ssd1306.SSD1306_I2C(128, 32, i2c)

x,y = 60,15
letter = []
def read_location():
    x_val = (read(0x33) << 8) | read(0x32)
    y_val = (read(0x35) << 8) | read(0x34)
    z_val = (read(0x37) << 8) | read(0x36)
    return x_val, y_val, z_val





def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        #wlan.connect('white horse club', 'gladpizza310')
        wlan.connect('Columbia University', '')
        while not wlan.isconnected():
            pass
    return wlan.ifconfig()



def show_time():
    display.fill(0)
    cur_date = "date: " + str(rtc.datetime()[0]) + '/' + str(rtc.datetime()[1]) + '/' + str(rtc.datetime()[2])#Date String
    cur_time = "time: " + str(rtc.datetime()[4]) + ':' + str(rtc.datetime()[5]) + ':' + str(rtc.datetime()[6])#Display Time
    display.text(cur_date, 0, 0)#Display Current date
    display.text(cur_time, 0, 10)#Display Current time
    display.show()#Show the display


i2c = I2C(sda=Pin(4), scl=Pin(5))#Set I2C connection
rtc = RTC()
display = ssd1306.SSD1306_I2C(128, 32, i2c)#Set details of display
#do_connect()#Do connection

# Define socket host and port
SERVER_HOST = do_connect()
SERVER_HOST = SERVER_HOST[0]
print(SERVER_HOST)
SERVER_PORT = 80


def trans_to_g(x):
    if x < 32768:
        y = x/(16384/2)
    else:
        y = -(65536 - x)/(16384/2)
    return y


# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create server_socket
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Set sockopt
s.bind((SERVER_HOST, SERVER_PORT)) # Bind SEVER_HOST AND SERVER_PORT
s.listen(1)
print('Listening on port %s ...' % SERVER_PORT) # SERVER_PORT = 80

# =============================================================================
# =============================================================================
Data = []
import urequests
#import csv
import json
while True:
# =============================================================================
# =============================================================================
# #     SERVER_HOST = do_connect()
# #     SERVER_HOST = SERVER_HOST[0]
# #     print(SERVER_HOST)
# =============================================================================
# =============================================================================
    # Wait for client connections
    client_connection, client_address = s.accept()
    print("Client connection is: ", client_connection, "Client address is:", client_address)
    print("Client has connected successfully.")

    # Get the client request
    request = client_connection.recv(1024).decode()
    print("request = ", request)
    #Print request of client
    global msg
    global resp_msg
    #global letter
    #global Data
    display_on = False
    display_time = False
    if 'data' in request:
        msg = request.split('/?data=')[1].split(' HTTP')[0]
        msg = msg.replace('%20', ' ')

        resp_msg = msg
        print("msg:",msg)
        #print(msg == 'turn on display')
        if 'record' in msg:
            utime.sleep(2)
            print("Recording started")
            for i in range(100):#record data
                x_val, y_val, z_val = read_location()
                x_g , y_g, z_g =  trans_to_g(x_val), trans_to_g(y_val), trans_to_g(z_val)
                letter.append((x_g, y_g, z_g))#record table tennis
                #letter.append(y_val)
                #print(x_val, y_val)
                utime.sleep(0.1)
            print("recording finished, Length of letter:", len(letter))
            #Data = Data.append(letter)
            print(letter)
            resp_msg = 'recording finished'
            continue
        
        elif 'test shakehand forehand' in msg:
            utime.sleep(2)
            print("Test shakehand forehand started")
            for i in range(100):
                x_val, y_val, z_val = read_location()
                x_g , y_g, z_g =  trans_to_g(x_val), trans_to_g(y_val), trans_to_g(z_val)
                letter.append(x_g)
                letter.append(y_g)
                #letter.append((x_g, y_g, z_g))#record table tennis
                #letter.append(y_val)
                #print(x_val, y_val)
                utime.sleep(0.1)
            print("Test shakehand forehand finished")
            output = {'input': letter}#shakehand forehand result
            print(len(output['input']))
            print(type(output['input']))
            json_str = json.dumps(output)

            url = 'http://129.236.150.159:5002/update_a_sf'
            #update shakehand forehand data in the server
            #url = 'http://192.168.1.204:5002/update_a_sf'
            res = urequests.put(url, data = json_str)
            print(res.text)
            result = eval(res.text)
            display.text(result["state"], 60, 15, 1)
            display.show()          
            resp_msg = 'text:' + msg
            letter = []
            break
            #continue
        
        elif 'test penhold forehand' in msg:
            utime.sleep(2)
            print("Test penhold forehand started")
            for i in range(100):
                x_val, y_val, z_val = read_location()
                x_g , y_g, z_g =  trans_to_g(x_val), trans_to_g(y_val), trans_to_g(z_val)
                letter.append(x_g)
                letter.append(y_g)
                #letter.append((x_g, y_g, z_g))#record table tennis
                #letter.append(y_val)
                #print(x_val, y_val)
                utime.sleep(0.1)
            print("Test penhold forehand finished")
            output = {'input': letter}#penhold forehand result
            print(len(output['input']))
            print(type(output['input']))
            json_str = json.dumps(output)

            #url = 'http://129.236.150.115:5001/update_a_pf'
            url = 'http://129.236.150.159:5002/update_a_pf'
            #update penhold forehand data in the server
            res = urequests.put(url, data = json_str)
            print(res.text)
            result = eval(res.text)
            display.text(result["state"], 60, 15, 1)
            display.show()          
            resp_msg = 'text:' + msg
            letter = []
            break
        
        
        elif 'test shakehand backhand' in msg:
            utime.sleep(2)
            print("Test shakehand backhand started")
            for i in range(100):
                x_val, y_val, z_val = read_location()
                x_g , y_g, z_g =  trans_to_g(x_val), trans_to_g(y_val), trans_to_g(z_val)
                letter.append(x_g)
                letter.append(y_g)
                #letter.append((x_g, y_g, z_g))#record table tennis
                #letter.append(y_val)
                #print(x_val, y_val)
                utime.sleep(0.1)
            print("Test shakehand backhand finished")
            #Data = Data.append(letter)
            #print(letter)
            output = {'input': letter}#shakehand backhand result
            print(len(output['input']))
            json_str = json.dumps(output)
            #url = 'http://129.236.150.115:5001/update_a_sb'
            url = 'http://129.236.150.159:5002/update_a_sb'
            # update shakehand backhand data in the server
            res = urequests.put(url, data = json_str)
            print(res.text)
            result = eval(res.text)
            display.text(result["state"], 60, 15, 1)
            display.show()          
            resp_msg = 'text:' + msg
            letter = []
            break
            #continue
        
        elif 'test penhold backhand' in msg:
            utime.sleep(2)
            print("Test penhold backhand started")
            for i in range(100):
                x_val, y_val, z_val = read_location()
                x_g , y_g, z_g =  trans_to_g(x_val), trans_to_g(y_val), trans_to_g(z_val)
                letter.append(x_g)
                letter.append(y_g)
                #letter.append((x_g, y_g, z_g))#record table tennis
                #letter.append(y_val)
                #print(x_val, y_val)
                utime.sleep(0.1)
            print("Test penhold backhand finished")
            #Data = Data.append(letter)
            #print(letter)
            output = {'input': letter}#penhold backhand result
            #print(len(output['input']))
            json_str = json.dumps(output)
            #url = 'http://129.236.150.115:5001/update_a_pb'#
            url = 'http://129.236.150.159:5002/update_a_pb'
            # update penhold backhand data in the server
            res = urequests.put(url, data = json_str)
            print(res.text)	
            result = eval(res.text)
            display.text(result["state"], 60, 15, 1)
            display.show()          
            resp_msg = 'text:' + msg
            letter = []
            break

            
        
        elif "evaluate" in msg:
        
            url = 'http://129.236.150.159:5002/search'
            res = ujson.loads(urequests.get(url).text)
            print(res)
            display.text('C:%.2f F:%.2f'%(res['consistency'], res['framework']), 0, 0, 1)
            display.text('T:%.2f A_B:%.2f'%(res['timing'], res['acceleration_backhand'],), 0, 12, 1)
            display.text('A_F:%.2f'%(res['acceleration_forehand']), 0, 24, 1)
            #display the evaluation, consistency, framework, timing, accelertion forehand, acceleration backhand at the end
            display.show()  
            
        elif 'output' in msg:
            output = {'letter': 'Backhand', 'data': letter}
            print(len(output['data']))
            letter = []
            #output.append(letter)
            #print(output)
            #print(output, type(output))
            json_str = json.dumps(output)
            #print(json_str, type(json_str))
            #url = 'http://44.201.205.246:5000/insert'
            url = 'http://129.236.150.159:5002/insert'
            res = urequests.put(url, data = json_str)
            print(res.text)
            resp_msg = 'text:' + msg    
            

        
            


        else:
            display_time = False
            print("Wrong Message")
            resp_msg = 'text:' + msg
            display.fill(0)
            display.text(resp_msg, 0, 0, 1)#Return what the user said
            display.show()


    # Send HTTP response

    response = 'HTTP/1.0 200 OK\n\n' + resp_msg
    client_connection.sendall(response.encode())
    client_connection.close()

# Close socket
s.close()

