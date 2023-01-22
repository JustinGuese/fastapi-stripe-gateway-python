# fastapi-stripe-gateway-python
a fastapi implementation of a stripe payment gateway using oauth proxy for authentication on kubernetes

needs stripe api key secret

kubectl create secret generic stripeapi --from-literal=STRIPE_API_KEY="sk_" -n paymentgateway-staging