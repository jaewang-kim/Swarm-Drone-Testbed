import attr
import natnet
from natnet.protocol.MocapFrameMessage import RigidBody

@attr.s
class ClientApp(object):

    _client = attr.ib()
    _quiet = attr.ib()

    _last_printed = attr.ib(0)

    @classmethod
    def connect(cls, server_name, rate, quiet):
        if server_name == 'fake':
            client = natnet.fakes.SingleFrameFakeClient.fake_connect(rate=rate)
        elif server_name == 'fake_v2':
            client = natnet.fakes.SingleFrameFakeClient.fake_connect_v2(rate=rate)
        else:
            client = natnet.Client.connect(server_name)
        if client is None:
            return None
        return cls(client, quiet)

    def run(self):
        if self._quiet:
            self._client.set_callback(self.callback_quiet)
        else:
            self._client.set_callback(self.callback)
        self._client.spin()


    def callback(self, rigid_bodies, skeletons, markers, timing):
        """
        :type rigid_bodies: list[RigidBody]
        :type rigid_bodies: list[Skeleton]
        :type markers: list[LabelledMarker]
        :type timing: TimestampAndLatency
        """
        global g_tracking_information
        global NUMOF_NODES

        # print('{:.4f}s: Received mocap frame'.format(timing.timestamp))  # for debug
        if rigid_bodies:
            # print('Rigid bodies:')
            # for b in sorted(rigid_bodies, key=lambda b: b.id_):
            if len(rigid_bodies) != NUMOF_NODES:
                raise Exception('The number of operating robots intended and the number of robots imported from Opti-track are different!\
                Check the registered RigidBody and NUMOF_NODES variables in the Opti-track Motive Program-Asset window')

            for body in rigid_bodies:
                
                if int(body.id_) in g_tracking_information.keys():
                    # 글로벌 변수 tracking_infomation[i]에 값 업데이트(크기 1짜리 큐라고 생각하면 될듯. 외부에서 볼 땐 항상 최신값만 저장되어있다.)
                    g_tracking_information[int(body.id_)] = body
                else:
                    raise Exception('None of the node numbers generated match the Streaming ID of the Optitrack-Motive program.\
                    Check the robot_index and robots declaration again in the Main function.')

g_tracking_information = None
NUMOF_NODES = None
def create_motion_tracker(server_name = '127.0.0.1', g_track_info:dict=None, rate = 100, quiet = None):
    global g_tracking_information
    global NUMOF_NODES

    g_tracking_information = g_track_info
    NUMOF_NODES = len(g_track_info.keys())
    try:
        motion_tracker = ClientApp.connect(server_name, rate, quiet)
        motion_tracker._client.set_callback(motion_tracker.callback)
        
        return motion_tracker
    
    except (KeyboardInterrupt, SystemExit):
        motion_tracker._client._log.info('Exiting')
    except natnet.DiscoveryError as e:
        print('Error:', e)

def tracking_position(motion_tracker):
    try:
        motion_tracker._client.run_once()
    except (KeyboardInterrupt, SystemExit):
        motion_tracker._client._log.info('Exiting')
    except natnet.DiscoveryError as e:
        print('Error:', e)


def tracking_position_original(server_name = '127.0.0.1', rate = 100, quiet = None):
    global g_flag_tracking
    try:
        motion_tracker = ClientApp.connect(server_name, rate, quiet)
        motion_tracker._client.set_callback(motion_tracker.callback)
        # Continuously receive and process messages
        while g_flag_tracking:
            # update positions of robots
            motion_tracker._client.run_once()

    except (KeyboardInterrupt, SystemExit):
        motion_tracker._client._log.info('Exiting')
    except natnet.DiscoveryError as e:
        print('Error:', e)