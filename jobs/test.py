from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("HDFS-Test-Job") \
    .getOrCreate()

# =========================
# 1. Read CSV from HDFS
# =========================

input_path = "hdfs://10.68.71.113:8020/data/input/test.csv"

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(input_path)

print("===== INPUT DATA =====")
df.show(10, truncate=False)

print("===== SCHEMA =====")
df.printSchema()

# =========================
# 2. Count rows
# =========================

row_count = df.count()

print("===== NUMBER OF ROWS =====")
print(row_count)

# =========================
# 3. Simple Spark processing
#    Group passengers by Sex
# =========================

result = df.groupBy("Sex").count()

print("===== RESULT: PASSENGERS BY SEX =====")
result.show()

# =========================
# 4. Write result to HDFS
# =========================

output_path = "hdfs://10.68.71.113:8020/data/output/test-result"

result.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(output_path)

print("===== JOB FINISHED =====")

spark.stop()