<html>
<head></head>
<body>
%if len(data):
%	for dat in data:
	<h4><a href="/info/{{dat['VaultName']}}/">{{dat['VaultName']}}</a></h4>
%	end
</body>
</html>