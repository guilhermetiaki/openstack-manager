#!/bin/bash

case $1 in
	add)
		./add_user.py ${@:2}
		;;
	delete)
		./delete_user.py ${@:2}
		;;
	disable)
		./enable_disable_user.py --disable ${@:2}
		;;
	enable)
		./enable_disable_user.py --enable ${@:2}
		;;
	*)
		echo "Usage: $0 {add|delete|disable|enable}"
		exit
		;;
esac
