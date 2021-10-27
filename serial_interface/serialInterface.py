import rclpy
import serial
import sys
import glob
from rclpy.node import Node
from std_msgs.msg import String


class CommandSubscriber(Node):

    def __init__(self):
        super().__init__('command_subscriber')

        self.subscription = self.create_subscription(
            String,
            'commands',
            self.listener_callback,
            10)

        serial_ports = self.get_serial_ports()

        self.ser = serial.Serial(serial_ports[0], baudrate= 9600,
           timeout=2.5,
           parity=serial.PARITY_NONE,
           bytesize=serial.EIGHTBITS,
           stopbits=serial.STOPBITS_ONE
        )

        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        # write command to serial
        self.get_logger().info('Received: "%s"' % msg.data)
        self.ser.flush()
        self.ser.write(msg.data.encode('ascii'))

        # print response
        incoming = self.ser.readline().decode("utf-8")
        self.get_logger().info('Robot: "%s"' % incoming )
    
    def get_serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
            
        return result


def main(args=None):
    rclpy.init(args=args)

    commandSubscriber = CommandSubscriber()

    rclpy.spin(commandSubscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    commandSubscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()