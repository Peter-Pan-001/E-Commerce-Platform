import pyspark.sql

spark = SparkSession.builder.appName("Queries").getOrCreate()

# read in tables from hdfs csv

customers_schema = StructType([
    StructField("customer_id", IntegerType(), True),
    StructField("address", StringType(), True)])
customers_df = spark.read.csv("hdfs:///user/peterpan/w4111/customers.csv",header=False,schema=customers_schema)

sellers_schema = StructType([
    StructField("seller_id", IntegerType(), True),
    StructField("address", StringType(), True)])
sellers_df = spark.read.csv("hdfs:///user/peterpan/w4111/sellers.csv",header=False,schema=sellers_schema)

products_schema = StructType([
    StructField("product_id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("description", StringType(), True),
    StructField("seller_id", IntegerType(), True),
    StructField("price", DoubleType(), True),
    StructField("quantity", StringType(), True)])
products_df = spark.read.csv("hdfs:///user/peterpan/w4111/products.csv",header=False,schema=products_schema)

orders_schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True)])
orders_df = spark.read.csv("hdfs:///user/peterpan/w4111/orders.csv",header=False,schema=orders_schema)

coupons_schema = StructType([
    StructField("coupon_id", IntegerType(), True),
    StructField("dicount", DoubleType(), True),
    StructField("seller_id", IntegerType(), True)])
coupons_df = spark.read.csv("hdfs:///user/peterpan/w4111/coupons.csv",header=False,schema=coupons_schema)

coupon_applied_schema = StructType([
    StructField("coupon_id", IntegerType(), True),
    StructField("product_id", IntegerType(), True)])
coupon_applied_df = spark.read.csv("hdfs:///user/peterpan/w4111/coupon_applied.csv",header=False,schema=coupon_applied_schema)

orders_products_schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("quantity", IntegerType(), True)])
orders_products_df = spark.read.csv("hdfs:///user/peterpan/w4111/orders_products.csv",header=False,schema=orders_products_schema)


# select the top 10 most popular customers in terms of number of products purchased

tmp_join = customers_df
                .join(orders_df, "customer_id")
                .select(customers_df.customer_id, orders_df.order_id)
join_1 = tmp_join
                .join(orders_products_df, "order_id")
                .select(temp_join.customer_id, orders_products_df.quantity)
popular_customers = join_1
                .groupBy("customer_id")
                .sum("quantity")
                .select("customer_id", functions.func.col("sum(quantity)").alias("sumQuantity"))
                .orderBy("sumQuantity", ascending = False)
                .take(10)

popular_customers.coalesce(1).write.format('json').save('hdfs:///user/peterpan/w4111/popular_customers.json')


# select the top 10 most popular sellers in terms of number of products sold

tmp_join = sellers_df
                .join(products_df, "seller_id")
                .select(sellers_df.seller_id, products_df.product_id)
join_2 = tmp_join
                .join(orders_products_df, "product_id")
                .select(temp_join.seller_id, orders_products_df.quantity)
popular_sellers = join_2
                .groupBy("seller_id")
                .sum("quantity")
                .select("seller_id", functions.func.col("sum(quantity)").alias("sumQuantity"))
                .orderBy("sumQuantity", ascending = False)
                .take(10)

popular_sellers.coalesce(1).write.format('json').save('hdfs:///user/peterpan/w4111/popular_sellers.json')


# select the top 10 customers in terms of total price purchased

discounted_products = coupons_df
                        .join(coupon_applied_df, "coupon_id")
                        .select(coupons_df.discount, coupon_applied_df.product_id)
                        .join(products_df, "product_id")
                        .select(coupons_df.discount, products_df.product_id, products_df.price)
                        .select(products_df.product_id.alias("product_id"), (products_df.price * (1 - coupons_df.discount)).alias("price"))
final_price = products_df
                    .select("product_id", "price")
                    .union(discounted_products)
                    .groupBy("product_id")
                    .min("price")
                    .select("product_id", functions.func.col("min(price)").alias("price"))

final_price.coalesce(1).write.format('json').save('hdfs:///user/peterpan/w4111/final_price.json')

popular_customers_price = customers_df
                                .join(orders_df, "customer_id")
                                .join(orders_products_df, "order_id")
                                .join(final_price, "product_id")
                                .groupBy(customers_df.customer_id)
                                .sum("price")
                                .select(customers_df.customer_id, functions.func.col("sum(price)").alias("total_price"))
                                .orderBy("total_price", ascending = False)
                                .take(10)

popular_customers_price.coalesce(1).write.format('json').save('hdfs:///user/peterpan/w4111/popular_customers_price.json')





