import objc
from datetime import datetime
import speedtest
megabit = 1048576


objc.loadBundle('CoreWLAN',
                bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                module_globals=globals())


def wifi():
    objc.loadBundle('CoreWLAN',
                    bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                    module_globals=globals())

    i_name = 'en0'
    interface = CWInterface.interfaceWithName_(i_name)
    date, network, rssi = None, None, None

    if interface is not None:
        network = interface.ssid()
        rssi = interface.rssi()
        date = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    else:
        print('No network')

    return date, network, rssi


def measure_speed():
    st = speedtest.Speedtest()
    down = st.download()
    up = st.upload()
    ping = st.results.ping
    return down, up, ping


def check_internet(format_num=0):
    date, network, rssi = wifi()
    down, up, ping = measure_speed()
    data = (date, network, rssi, ping, round(up/megabit), round(down/megabit))
    format_0 = "%s, %s, %s, %s, %s, %s"
    format_1 = "%s Network: %s, RSSI: %s, Ping: %0.2f, Upload: %s, Download: %s"
    formats = [format_0, format_1]
    print(formats[format_num] % data)


if __name__ == "__main__":
    check_internet(format_num=1)
