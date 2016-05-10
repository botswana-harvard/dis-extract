function home() {
	$.ajax({
		type:'GET',
		url:"{% url 'home' %}",
		data:{
			action:"select_protocol",
		},
		success:function(json){
            $("#id-protocol-form").show();
			$("#pill-home").hide();
			$("#pill-received").hide();
			$("#pill-resulted").hide();
			$("#pill-stored").hide();
			$("#txt-protocol").text("");
		}
	});
	return true;
}

function receivedHome() {
	$.ajax({
		type:'GET',
		url:"{% url 'home' %}",
		data:{
			action:"select_protocol",
		},
		success:function(json){
			$("#pill-home").hide();
			$("#pill-received").show();
			$("#txt-protocol").text(json.protocol);
		}
	});
	return true;
}

function resultedHome() {
	$.ajax({
		type:'GET',
		url:"{% url 'home' %}",
		data:{
			action:"select_protocol",
		},
		success:function(json){
			$("#pill-home").hide();
			$("#pill-resulted").show();
			$("#txt-protocol").text(json.protocol);
		}
	});
	return true;
}

function storedHome() {
	$.ajax({
		type:'GET',
		url:"{% url 'home' %}",
		data:{
			action:"select_protocol",
		},
		success:function(json){
			$("#pill-home").hide();
			$("#pill-stored").show();
			$("#txt-protocol").text(json.protocol);
		}
	});
	return true;
}

function protocolHome() {
	$.ajax({
		type:'GET',
		url:"{% url 'home' %}",
		data:{
			action:"select_protocol",
		},
		success:function(json){
			$("#pill-home").show();
			$("#pill-received").hide();
			$("#pill-resulted").hide();
			$("#pill-stored").hide();
			$("#txt-protocol").text(json.protocol);
		}
	});
	return true;
}
