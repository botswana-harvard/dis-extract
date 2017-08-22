/*!
 dmis-extract custom js functions
*/

function homeReady() {
    $( '#id-page-heading' ).text( 'BHHRL' );
    $('[id^="div-dmis-"]').hide();
    $( '#div-dmis-home' ).show();
    $( '#pill-received-label' ).hide();    
    $( '#btn-data-table-done' ).click( function(e) { resetDataTable(e); });
    $( '#pill-received-most-recent' ).click(function(e){
        mostRecent(e, "{% url 'home' %}", 1);
    });
    $( '#id-protocol-form' ).ajaxForm({
        success: function(data) { 
              if (data.protocol != '') {
                  $("#id-protocol-form").hide();
                  $("#txt-protocol").text(data.protocol);
                  $("#pill-protocol").text(data.protocol);
                  $("#pill-home").show();
                  $("#id-protocol-title").text(data.protocol_title);
              } else {
                  $("#pill-home").hide();
                  $("#txt-protocol").text(data.protocol);
                  $("#pill-protocol").text(data.protocol);
                  $("#id-protocol-title").text('Protocol not found');
              }
            },
    });	
}

function resetDataTable(e) {
    $("#data-table thead").html("");
    $("#data-table tbody").html("");
    $("#div-data-table").toggle();
    $("#pill-received-label").hide();
    $("#pill-received-most-recent").removeClass('disabled');
    $("#pill-received-most-recent").show();
    $("#pill-received-pending").show();
    $("#pill-received-label").hide();
    return true;
}

function mostRecent(e, url, page) {
    $("#pill-received-pending").hide();
    $("#pill-received-most-recent").hide();
    $("#pill-received-label").html("<a href=\"#\">Most Recent</a>");
    $("#pill-received-label").show()
    $('#alert-fetching').show();    
    var protocol=$("#pill-protocol").text();
    $.ajax({
        type:'GET',
        url: url,
        data:{
            action:"received-most-recent",
            protocol: $("#pill-protocol").text(),
            page: page,
        },
        success: function(json) {
            $('#alert-fetching').hide();
            $("#data-table thead").html(json.thead);
            $("#data-table tbody").html(json.tbody);
            $("#div-data-table").toggle();
        }
    });
    return true;
}

function labReportsHome(e) {
    $('[id^="div-dmis-"]').hide();
    $("#div-dmis-lab-reports-home").show();
    $("#div-dmis-lab-reports-billing").hide();
}

function coordinatorReportsHome(e) {
    $('[id^="div-dmis-"]').hide();
    $("#div-dmis-coordinator-reports-home").show();
}

function labReportsBilling () {
    $('[id^="div-dmis-"]').hide();
    $( '#div-dmis-lab-reports-billing' ).show();
    $( '#id-page-heading' ).text( 'Billing Report' );
}



function home() {
    $('[id^="div-dmis-"]').hide();
    $( '#id-page-heading' ).text('BHHRL');
    $( '#div-dmis-page-header' ).show()
    $( '#div-dmis-home' ).show();
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
};

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
};

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
};

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
};

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
};
