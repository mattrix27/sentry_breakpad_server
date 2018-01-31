import boto

def go():
	print('umm')
	bucket = boto.bucket_manager()
	bucket.walk()
go()