import argparse
import sys
from app import DeadManSwitch

def main():
    parser = argparse.ArgumentParser(description='Dead Man Switch CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create alert command
    create_parser = subparsers.add_parser('create', help='Create a new alert')
    create_parser.add_argument('--user-id', required=True, help='User ID')
    create_parser.add_argument('--id', required=True, help='Alert ID')
    create_parser.add_argument('--message', required=True, help='Message to send')
    create_parser.add_argument('--group-id', required=True, help='Telegram group/channel ID')
    create_parser.add_argument('--expiry', type=int, required=True, help='Days until expiry')
    create_parser.add_argument('--check-in', type=int, required=True, help='Days between check-ins')

    # Check-in command
    checkin_parser = subparsers.add_parser('checkin', help='Check in for an alert')
    checkin_parser.add_argument('--user-id', required=True, help='User ID')
    checkin_parser.add_argument('--id', required=True, help='Alert ID')

    # Trigger command
    trigger_parser = subparsers.add_parser('trigger', help='Manually trigger an alert')
    trigger_parser.add_argument('--user-id', required=True, help='User ID')
    trigger_parser.add_argument('--id', required=True, help='Alert ID')

    args = parser.parse_args()
    switch = DeadManSwitch()

    if args.command == 'create':
        alert_id = switch.create_alert(
            args.user_id,
            args.id,
            args.message,
            args.group_id,
            args.expiry,
            args.check_in
        )
        print(f"Created alert with ID: {alert_id}")
    
    elif args.command == 'checkin':
        if switch.check_in(args.user_id, args.id):
            print(f"Successfully checked in for alert: {args.id}")
        else:
            print(f"Failed to check in for alert: {args.id}")
            sys.exit(1)
    
    elif args.command == 'trigger':
        if switch.trigger_alert(args.user_id, args.id):
            print(f"Successfully triggered alert: {args.id}")
        else:
            print(f"Failed to trigger alert: {args.id}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 