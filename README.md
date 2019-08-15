# E-Commerce-Platform

## 1. ER Diagram

![](Part1_ER_Schema/Final.png)


## 2. Schema

users (user_id, name, gender, password)

customers (user_id, address)

sellers (user_id, address)

products (product_id, name, description, seller_id, price, quantity)

coupons (coupon_id, discount, seller_id)

orders (order_id, customer_id)

coupon_applied (coupon_id, product_id)

orders_products (order_id, product_id, quantity)


## 3. Functionality Queries

(1) Select the customer with the most products added

``
SELECT customers.user_id  
``
<br/>
``
FROM products, customers, carts  
``
<br/>
``
WHERE customers.use_id = carts.customer_id and 
	    carts.cart_id = products.cart_id  
``
<br/>
``
GROUP BY cutomers.user_id  
``
<br/>
``
ORDER BY count(*) DESC  
``
<br/>
``
LIMIT 1;  
``
<br/>

(2) Select the best seller in terms of the number of sold products

``
SELECT sellers.user_id 
``
<br/>
``
FROM sellers, products
``
<br/>
``
WHERE sellers.user_id = products.seller_id and 
     cart_id in (select cart_id from carts) 
``
<br/>
``
GROUP BY user_id
``
<br/>
``
ORDER BY count(*) DESC
``
<br/>
``
LIMIT 1;
``
<br/>

(3) Select the customer whose products are most expensive after using coupons

``
CREATE VIEW discounted_products AS(
``
<br/>
``
SELECT products.product_id, products.price * (1 -(coupons.discount))
``
<br/>
``
FROM products, coupons, coupon_applied
``
<br/>
``
WHERE coupons.coupon_id = coupon_applied.coupon_id and 
	   coupon_applied.product_id = products.product_id
);
``
<br/>

``
CREATE VIEW final_price AS(
``
<br/>
``
(SELECT product_id, price 
``
<br/>
``
 FROM products
``
<br/>
``
 WHERE product_id not in (SELECT product_id FROM discounted_products))
 ``
<br/>

``
UNION
``
<br/>

``
(SELECT * FROM discounted_products)
``
<br/>
``
);
``
<br/>

``
SELECT customers.user_id
``
<br/>
``
FROM products, customers, carts, final_price
``
<br/>
``
WHERE customers.user_id = carts.customer_id and
``
<br/>
``
	    carts.cart_id = products.cart_id and
      ``
<br/>
``
	    products.product_id = final_price.product_id
      ``
<br/>
``
GROUP BY customers.user_id
``
<br/>
``
ORDER BY sum(final_price.price) DESC
``
<br/>
``
LIMIT 1;
``
