from pubnub import Pubnub
def callback_1(message, channel):
	print(message)
pub_publish_key = "pub-c-381c302a-d433-48da-a4d8-2e4c52c651af"
pub_sub_key = "sub-c-08e2953c-bd8f-11e5-8408-0619f8945a4f"
pub_secret_key = "sec-c-MWQ2NGQ3ZTgtYmFlMS00NTFmLWIzYzItNGE5YzkzMTM5NGY4"
CHANNEL = 'chart-data'
instance = Pubnub(publish_key=pub_publish_key, subscribe_key=pub_sub_key)

print('listening on channel', CHANNEL)
instance.subscribe(CHANNEL, callback_1)