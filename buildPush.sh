#!/bin/bash
docker build -t guestros/stripe-payment-backend:latest .
docker push guestros/stripe-payment-backend:latest