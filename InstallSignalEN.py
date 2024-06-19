#!/usr/bin/env python
#coding: utf-8
#
# Run this file with superuser rights ('sudo') to install the Signal client

input("Did you run this script with super user rights ('sudo'), Press enter to continue")
input("Welcome to the signal-cli install wizard.\nPress ENTER when you are ready.")

import os


javaInstalled = input("\n\nSignal requires Java, install with sudo apt install openjdk-21-jre \nIs Java correctly installed? (Yes/No): ")

if javaInstalled in ['Oui', 'Yes', 'O', 'Y', 'oui', 'yes', 'o', 'y']:

	# Ask for Signal number and check if input is matching the required format
	numberOK = False
	while not numberOK:
		number = input("""\nType in the phone number that will be associated to your Signal account.\nThis nimber must be formatted as follows: +CCXXXXXXXXX (CC : Country Code).\ne.g. for France: +33601020304.\nNumber: """)
		numberOK = True
		if number[0] != '+':
			numberOK = False
		else:
			for i in range(1,len(number)):
				if number[i] not in ['0', '1', '2', '3', '4','5', '6', '7', '8', '9']:
					numberOK = False
		if numberOK == False:
			print("\nThis is not a valid number. Please retry.")

	# Ask for Signal version and check if input is matching the required format
	versionOK = False
	while not versionOK:
		version = input("""\nPlease check the latest signal-cli version\non https://github.com/AsamK/signal-cli/releases and write it below.\nThe format must be x.y.z. e.g. : 0.6.2\nVersion: """)
		versionOK = True
		# if len(version) != 5 or version[1] != '.' or version[3] != '.':
		# 	versionOK = False
		# else:
		# 	for i in [0,2,4]:
		# 		if version[i] not in ['0', '1', '2', '3', '4','5', '6', '7', '8', '9']:
		# 			versionOK = False
		# if versionOK == False:
		# 	print("\nThis is not a valid number. Please retry.")


	os.system("cd /tmp ; wget https://github.com/AsamK/signal-cli/releases/download/v" + version + "/signal-cli-" + version + ".tar.gz")
	os.system("tar xf /tmp/signal-cli-" + version + ".tar.gz -C /opt ; ln -sf /opt/signal-cli-" + version + "/bin/signal-cli /usr/local/bin/")
	os.system('apt-get install -y git')
	os.system("cd /tmp ; git clone https://github.com/AsamK/signal-cli.git")
	os.system("cd /tmp/signal-cli/data ; cp org.asamk.Signal.conf /etc/dbus-1/system.d/ ; cp org.asamk.Signal.service /usr/share/dbus-1/system-services/ ; cp signal-cli.service /etc/systemd/system/")
	os.system("""sed -i -e "s|%dir%|/opt/signal-cli-""" + version + """/|" -e "s|%number%|""" + number + """|" /etc/systemd/system/signal-cli.service""")

	os.system("""sed -i -e 's|policy user="signal-cli"|policy user="root"|' /etc/dbus-1/system.d/org.asamk.Signal.conf""")
	os.system("""sed -i -e 's|User=signal-cli|User=root|' /etc/systemd/system/signal-cli.service""")
	installMode = input("\nA Signal account might be installed on several devices.\nIn this case, one of them is the master device,\nand the others must be linked via a QR Code before use.\nWill this computer be used as the master device for your Signal account? (Yes/No): ")

	if installMode in ['Oui', 'Yes', 'O', 'Y', 'oui', 'yes', 'o', 'y']:
		sms = input("\nA validation PIN will be sent to the provided phone number.\nIf this phone cannot receive SMS (landline), the PIN will be given by a call.\nCan this phone number receive SMS? (Yes/No): ")
		if sms in ['Oui', 'Yes', 'O', 'Y', 'oui', 'yes', 'o', 'y']:
			os.system("signal-cli --config /var/lib/signal-cli -u " + number + " register")
		else:
			os.system("signal-cli --config /var/lib/signal-cli -u " + number + " register --voice")

		# Ask for verfication code and check if input is matching the required format
		verifOK = False
		while not verifOK:
			verifCode  = input("Enter the 6-digit validation PIN you just received: ")
			verifOK = True
			if len(verifCode) != 6:
				verifOK = False
			else:
				for i in range(6):
					if verifCode[i] not in ['0', '1', '2', '3', '4','5', '6', '7', '8', '9']:
						verifOK = False
			if verifOK == False:
				print("\nThis is not a valid number. Please retry.")

		os.system('signal-cli --config /var/lib/signal-cli -u ' + number + ' verify ' + verifCode)

	else:
		deviceName = input("""\nYou are about to generate a link beginning by tsdevice://...\nCopy it and paste it in a QR Code generator, like https://www.qrcode-generator.de/.\nBe careful not to choose "URL" in the generator.\nUse the Signal app on your phone to flash the generated QR code.\nHow do you ant to name your device?: """)
		os.system('''signal-cli --config /var/lib/signal-cli link -n "''' + deviceName + '''"''')

	os.system("apt-get install libunixsocket-java")
	os.system("cp /usr/lib/jni/libunix-java.so /lib") # Because sometimes it says that libunix-java is not in java.library.path
	os.system("systemctl daemon-reload && systemctl enable signal-cli.service && systemctl reload dbus.service && systemctl start signal-cli.service")

	print("\nInstallation finished.")

	numberOK = False
	while not numberOK:
		number = input("\nIn order to check if the installation completed correctly,\nplease provide a phone number linked to a Signal account (not this one).\nThis number must be formatted as follows: +CCXXXXXXXXX (CC : Country Code).\ne.g. for France: +33601020304.\nNumber: ")
		numberOK = True
		if number[0] != '+':
			numberOK = False
		else:
			for i in range(1,len(number)):
				if number[i] not in ['0', '1', '2', '3', '4','5', '6', '7', '8', '9']:
					numberOK = False
		if numberOK == False:
			print("\nThis is not a valid number. Please retry.")
		else:
			os.system('''signal-cli --config /var/lib/signal-cli --dbus-system send -m "Everything works as expected. The signal-cli client installation is finished.\nWell done!" ''' + number)
			received = input("\nA message has just been sent to this number.\nHave you received it? (Yes/No): ")
			if received not in ['Oui', 'Yes', 'O', 'Y', 'oui', 'yes', 'o', 'y']:
				numberOK = False
