#!/bin/bash

# Define recipient emails
ADMIN_EMAIL="abc@example.com"


# Send the full NUT alert message to Jamie
echo -e "Subject: UPS ALERT: $NOTIFYTYPE\n\n$*\r\n" | msmtp $ADMIN_EMAIL




