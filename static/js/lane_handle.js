function point_it(event){
	pos_x = event.offsetX?(event.offsetX):event.pageX-document.getElementById("pointer_div").offsetLeft;
	pos_y = event.offsetY?(event.offsetY):event.pageY-document.getElementById("pointer_div").offsetTop;
	document.getElementById("cross").style.left = (pos_x-1) ;
	document.getElementById("cross").style.top = (pos_y-15) ;
	document.getElementById("cross").style.visibility = "visible" ;
	console.log($("#pos_select").html() );
	if ($("#pos_select").html() == '0'){
	    document.pointform.up_left_x.value = pos_x;
	    document.pointform.up_left_y.value = pos_y;
	    $("#pos_select").html('1');
	}
	else if ($("#pos_select").html() == '1'){
	    document.pointform.up_right_x.value = pos_x;
	    document.pointform.up_right_y.value = pos_y;
	    $("#pos_select").html('2');
	}
	else if ($("#pos_select").html() == '2'){
	    document.pointform.low_left_x.value = pos_x;
	    document.pointform.low_left_y.value = pos_y;
	    $("#pos_select").html('3');
	}
	else if ($("#pos_select").html() == '3'){
	    document.pointform.low_right_x.value = pos_x;
	    document.pointform.low_right_y.value = pos_y;
	    $("#pos_select").html('0');
	}
}

function draw_line(event){
    var canvas = document.getElementById("pointer_div");
    var ctx = canvas.getContext("2d");

    var ulx = $("#up_left_x").val();
    var urx = $("#up_right_x").val();
    var llx = $("#low_left_x").val();
    var lrx = $("#low_right_x").val();

    var uly = $("#up_left_y").val();
    var ury = $("#up_right_y").val();
    var lly = $("#low_left_y").val();
    var lry = $("#low_right_y").val();
    ctx.beginPath();
    ctx.moveTo(ulx, uly);
    ctx.lineTo(urx, ury);
    ctx.lineTo(lrx, lry);
    ctx.lineTo(llx, lly);
    ctx.lineTo(ulx, uly);
    ctx.lineWidth=3;
    ctx.strokeStyle = "#01DF01";
    ctx.stroke();
}

function clear_line(event){
    var canvas = document.getElementById("pointer_div");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function add_lane(event){
    var ulx = $("#up_left_x").val();
    var urx = $("#up_right_x").val();
    var llx = $("#low_left_x").val();
    var lrx = $("#low_right_x").val();

    var uly = $("#up_left_y").val();
    var ury = $("#up_right_y").val();
    var lly = $("#low_left_y").val();
    var lry = $("#low_right_y").val();

    var laneObj ={};
    laneObj["up_left"  ] = [ulx, uly];
    laneObj["up_right" ] = [urx, ury];
    laneObj["low_left" ] = [llx, lly];
    laneObj["low_right"] = [lrx, lry];


    if(typeof Storage !== "undefined") {
        if (sessionStorage.getItem('lane')) {
            var lane = JSON.parse(sessionStorage.getItem("lane"));
            lane.push(laneObj);
            sessionStorage.setItem('lane', JSON.stringify(lane));
        } else {
            var lane = [];
            lane.push(laneObj);
            sessionStorage.setItem('lane', JSON.stringify(lane));
        }
    }
}

function remove_lane(event){
    sessionStorage.removeItem('lane');
}