
/* global map varaible */
var map;
var now;
var mode = "profile";
var source = "all";
var detail_chart_mode = "timeseries";
var current_device_id = "";
var old_device_id = "";
var current_start_date = "";
var current_end_date = "";
var current_query_length = 12;
var current_lower_limit_of_the_number_of_single_motif = 2;
var current_time_mode = "day";

var compute = false;

var pos2device = new Object();

var device2name = new Object();

var device2s_d0 = new Object();

var device2s_t0 = new Object();

var device2s_h0 = new Object();

function initial_map()
{
	var southWest = L.latLng(-90, -180);
	var northEast = L.latLng(90, 180);
	var bounds = L.latLngBounds(southWest, northEast);

	map = L.map('map', {
								   center:[24.785838418511574, 120.99483489990233],
								   zoom: 12,
								   maxBounds: bounds,
								   layers: [],
								   crs: L.CRS.EPSG3857
								 });
								 

	var title_layer = L.tileLayer(
		'http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', 
		{
			maxZoom: 18,
			minZoom: 1,
			attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			detectRetina: false
			}
		).addTo(map);

    // hide the input parameter for the detail chart
    document.getElementById("same").style.visibility = "hidden";
    document.getElementById("different_motif").style.visibility = "hidden";
    document.getElementById("different_average_max_min").style.visibility = "hidden";
    document.getElementById("go").style.visibility = "hidden";
}


function clear_map(){	
	$.each(map._layers, function (ml) {		
			if (map._layers[ml]._animated != true )
			{
				//console.log(map._layers[ml])
				map.removeLayer(map._layers[ml])
			}			
		})		
}



function detail_chart(id){
	/*
	console.log('name: ' + device2name[id])
	console.log('PM25: ' + device2s_d0[id])
	console.log('humidity: ' + device2s_h0[id])
	console.log('temperature: ' + device2s_t0[id])
	*/
	
	console.log("detail_chart_mode = " + detail_chart_mode + ", device_id = " + id);

	//clear plotly

    Plotly.purge('detail_information');

    //haven't select any device
	if (id == "")
	    return;
	
	if (mode == "profile") {
        if(id == device2name[id])
            $("#name").text("名稱:"+id);
        else
            $("#name").text("名稱:"+id + "  " + device2name[id]);

        $("#info").text("PM2.5:" + device2s_d0[id]+ "μg/m^3"  + "   氣溫:" +  device2s_t0[id] + "℃" + "   濕度:" + device2s_h0[id] + "%");

        if (detail_chart_mode == "timeseries")
        {
            recent_data = get_recent_data(id)



            time = [];
            PM25_value = [];
            temperature_value = [];
            humidity_value = [];

            for (var i = 0; i < recent_data.length; i++)
            {
                time.push(recent_data[i]['timestamp']);
                PM25_value.push(recent_data[i]['pm25']);
                temperature_value.push(recent_data[i]['temperature']);
                humidity_value.push(recent_data[i]['humidity']);
            }


            var layout =
                {
                    xaxis: {
                        title: 'Time',
                        gridcolor:'gray',
                        linecolor:'gray',
                        titlefont: {color: 'white',size:'18'},
                        tickfont: {color: 'white',size:'15'},
                        domain: [0.05, 0.925]
                    },
                    yaxis: {
                        title: 'PM2.5 μg/m^3',
                        linecolor:'red',
                        tickcolor:'red',
                        titlefont: {color: 'red',size:'18'},
                        tickfont: {color: 'red',size:'15'}
                    },
                    yaxis2: {
                        title: '溫度',
                        linecolor:'orange',
                        tickcolor:'orange',
                        titlefont: {color: 'orange',size:'18'},
                        tickfont: {color: 'orange',size:'15'},
                        anchor: 'x',
                        side:'right',
                        overlaying: 'y'
                    },
                    yaxis3: {
                        title: '濕度',
                        linecolor:'yellow',
                        tickcolor:'yellow',
                        titlefont: {color: 'yellow',size:'18'},
                        tickfont: {color: 'yellow',size:'15'},
                        side:'right',
                        overlaying: 'y',
                        anchor: 'free',
                        position: 1
                    },
                    margin: {t: 20},
                    hovermode: 'closest',
                    paper_bgcolor:'#3c5a98',
                    plot_bgcolor:'#3c5a98',
                    legend: {
                        x:1.05,
                        y:1,
                        //traceorder: 'normal',
                        font: {
                            family: 'sans-serif',
                            size: 15,
                            color: 'white'
                        },
                    }
                };



            var PM25_data =
                {
                    x: time,
                    y: PM25_value,
                    name: 'PM25',
                    type: 'scatter',
                    line: {
                        //width: 3,
                        color: 'red'
                    }
                }


            var temperature_data =
                {
                    x: time,
                    y: temperature_value,
                    name: '溫度',
                    type: 'scatter',
                    line: {
                        //width: 3,
                        color: 'orange'
                    },
                    yaxis: 'y2',
                };

            var humidity_data =
                {
                    x: time,
                    y: humidity_value,
                    name: '濕度',
                    type: 'scatter',
                    line: {
                        //width: 3,
                        color: 'yellow'
                    },
                    yaxis: 'y3',
                };

            var trace = [PM25_data, temperature_data, humidity_data]

            //"detail_information" is the slider_content
            Plotly.newPlot('detail_information', trace, layout, {showLink: false});
        }
        else if (detail_chart_mode == "motif" && compute == true)
        {
            compute = false;

            start_date = current_start_date;
            end_date = current_end_date;
            query_length = current_query_length;
            number_of_motifs = 3;
            lower_limit_of_the_number_of_single_motif = current_lower_limit_of_the_number_of_single_motif;

            matrix_profile_data = get_matrix_profile_data(id, start_date, end_date, 5, query_length, "mass", number_of_motifs, lower_limit_of_the_number_of_single_motif);



            motif_data = [];
            timestamp = [];

            for (var index_number_of_motifs = 0; index_number_of_motifs < number_of_motifs; index_number_of_motifs++)
            {
                motif_data.push([]);
                timestamp.push([]);
                for (var index_number_of_single_motif = 0; index_number_of_single_motif < matrix_profile_data["motif_index"][index_number_of_motifs].length; index_number_of_single_motif++)
                {
                    motif_data[index_number_of_motifs].push([]);
                    //timestamp[index_number_of_motifs].push([]);

                    timestamp[index_number_of_motifs].push(matrix_profile_data["timestamp"][matrix_profile_data["motif_index"][index_number_of_motifs][index_number_of_single_motif]]);
                    for (var index_query_length = 0; index_query_length < query_length; index_query_length++)
                    {
                        motif_data[index_number_of_motifs][index_number_of_single_motif]
                            .push(matrix_profile_data["pm25"][matrix_profile_data["motif_index"][index_number_of_motifs][index_number_of_single_motif] + index_query_length]);
                        //timestamp[index_number_of_motifs][index_number_of_single_motif]
                        //.push(matrix_profile_data["timestamp"][matrix_profile_data["motif_index"][index_number_of_motifs][index_number_of_single_motif] + index_query_length]);
                    }
                }
            }



            console.log("motif_data");
            console.log(motif_data);
            console.log("timestamp");
            console.log(timestamp);


            var layout = {
                xaxis: {
                    title: 'k = 1',
                    gridcolor:'gray',
                    linecolor:'gray',
                    titlefont: {color: 'white'},
                    tickfont: {color: 'white'},
                    domain: [0, 0.3],

                },
                yaxis: {
                    title: 'PM2.5',
                    gridcolor:'gray',
                    linecolor:'gray',
                    titlefont: {color: 'white'},
                    tickfont: {color: 'white'},
                    domain: [0, 1],
                    anchor: 'x'
                },

                xaxis2: {
                    title: 'k = 2',
                    gridcolor:'gray',
                    linecolor:'gray',
                    titlefont: {color: 'white'},
                    tickfont: {color: 'white'},
                    domain: [0.35, 0.65]
                },
                yaxis2: {
                    gridcolor:'gray',
                    linecolor:'gray',
                    titlefont: {color: 'white'},
                    tickfont: {color: 'white'},
                    domain: [0, 1],
                    anchor: 'x2'
                },

                xaxis3: {
                    title: 'k = 3',
                    gridcolor:'gray',
                    linecolor:'gray',
                    titlefont: {color: 'white'},
                    tickfont: {color: 'white'},
                    domain: [0.7, 1]
                },
                yaxis3: {
                    gridcolor:'gray',
                    linecolor:'gray',
                    titlefont: {color: 'white'},
                    tickfont: {color: 'white'},
                    domain: [0, 1],
                    anchor: 'x3'
                },

                margin: {t: 30},
                hovermode: 'closest',
                paper_bgcolor:'#3c5a98',
                plot_bgcolor:'#3c5a98',
                legend: {
                    x:1.05,
                    y:1,
                    //traceorder: 'normal',
                    font: {
                        family: 'sans-serif',
                        //size: 15,
                        color: 'white'
                    },
                }
            };


            var x_query_length = [];
            for (var i = 0; i < query_length; i++)
            {
                x_query_length.push(i);
            }
            //console.log(x_query_length);

            var trace = []

            for (var index_number_of_motifs = 0; index_number_of_motifs < number_of_motifs; index_number_of_motifs++)
            {
                for (var index_number_of_single_motif = 0; index_number_of_single_motif < motif_data[index_number_of_motifs].length; index_number_of_single_motif++)
                {
                    if (index_number_of_motifs == 0)
                    {
                        //console.log(timestamp[index_number_of_motifs][index_number_of_single_motif]);
                        trace.push(
                            {
                                x: x_query_length,
                                y: motif_data[index_number_of_motifs][index_number_of_single_motif],
                                name: "(k = " + (index_number_of_motifs + 1) + ") " + timestamp[index_number_of_motifs][index_number_of_single_motif],
                                text: timestamp[index_number_of_motifs][index_number_of_single_motif],
                                type: 'scatter',
                                hoverinfo:'y+text'
                            }
                        );
                    }
                    else if (index_number_of_motifs == 1)
                    {
                        trace.push(
                            {
                                x: x_query_length,
                                y: motif_data[index_number_of_motifs][index_number_of_single_motif],
                                name: "(k = " + (index_number_of_motifs + 1) + ") " + timestamp[index_number_of_motifs][index_number_of_single_motif],
                                text: timestamp[index_number_of_motifs][index_number_of_single_motif],
                                xaxis: 'x2',
                                yaxis: 'y2',
                                type: 'scatter',
                                hoverinfo:'y+text'
                            }
                        );
                    }
                    else if (index_number_of_motifs == 2)
                    {
                        trace.push(
                            {
                                x: x_query_length,
                                y: motif_data[index_number_of_motifs][index_number_of_single_motif],
                                name: "(k = " + (index_number_of_motifs + 1) + ") " + timestamp[index_number_of_motifs][index_number_of_single_motif],
                                text: timestamp[index_number_of_motifs][index_number_of_single_motif],
                                xaxis: 'x3',
                                yaxis: 'y3',
                                type: 'scatter',
                                hoverinfo:'y+text'
                            }
                        );
                    }
                }
            }


            //"detail_information" is the slider_content
            Plotly.newPlot('detail_information', trace, layout, {showLink: false});
        }
        else if (detail_chart_mode == "average_max_min" && compute == true)
        {
            compute = false;

            start_date = current_start_date;
            end_date = current_end_date;
            time_mode = current_time_mode

            average_max_min_data = get_average_max_min_data(id, start_date, end_date, 5, time_mode)


            var layout =
                {
                    xaxis: {
                        title: 'Time',
                        gridcolor:'gray',
                        linecolor:'gray',
                        titlefont: {color: 'white',size:'18'},
                        tickfont: {color: 'white',size:'8'},
                        domain: [0.05, 0.925]
                    },
                    yaxis: {
                        title: '平均',
                        linecolor:'red',
                        tickcolor:'red',
                        titlefont: {color: 'red',size:'18'},
                        tickfont: {color: 'red',size:'15'},
                        range: [0, Math.max.apply(Math, average_max_min_data['max_data'])]
                    },
                    yaxis2: {
                        title: '最大',
                        linecolor:'orange',
                        tickcolor:'orange',
                        titlefont: {color: 'orange',size:'18'},
                        tickfont: {color: 'orange',size:'15'},
                        anchor: 'x',
                        side:'right',
                        overlaying: 'y',
                        range: [0, Math.max.apply(Math, average_max_min_data['max_data'])]
                    },
                    yaxis3: {
                        title: '最小',
                        linecolor:'yellow',
                        tickcolor:'yellow',
                        titlefont: {color: 'yellow',size:'18'},
                        tickfont: {color: 'yellow',size:'15'},
                        side:'right',
                        overlaying: 'y',
                        anchor: 'free',
                        position: 1,
                        range: [0, Math.max.apply(Math, average_max_min_data['max_data'])]
                    },
                    margin: {t: 20},
                    hovermode: 'closest',
                    paper_bgcolor:'#3c5a98',
                    plot_bgcolor:'#3c5a98',
                    legend: {
                        x:1.05,
                        y:1,
                        //traceorder: 'normal',
                        font: {
                            family: 'sans-serif',
                            size: 15,
                            color: 'white'
                        },
                    }
                };



            var average_data =
                {
                    x: average_max_min_data['timestamp'],
                    y: average_max_min_data['average_data'],
                    name: '平均',
                    type: 'scatter',
                    line: {
                        //width: 3,
                        color: 'red'
                    }
                }


            var max_data =
                {
                    x: average_max_min_data['timestamp'],
                    y: average_max_min_data['max_data'],
                    name: '最大',
                    type: 'scatter',
                    line: {
                        //width: 3,
                        color: 'orange'
                    },
                    yaxis: 'y2',
                };

            var min_data =
                {
                    x: average_max_min_data['timestamp'],
                    y: average_max_min_data['min_data'],
                    name: '最小',
                    type: 'scatter',
                    line: {
                        //width: 3,
                        color: 'yellow'
                    },
                    yaxis: 'y3',
                };

            var trace = [average_data, max_data, min_data]

            //"detail_information" is the slider_content
            Plotly.newPlot('detail_information', trace, layout, {showLink: false});
        }
	}
	else if (mode == "radius") {

	}
	
}



function get_real_time_data() {
	var rdata;
	$.ajax({
		type: "GET",
        url: '../data/real_time_data/' + source + '.json',
		async: false,
		dataType: "json",
		success: function (data) {
			rdata = data;
            //console.log('../data/real_time_data/' + source + '.json');
		}
	});
	
	console.log(rdata);
	return rdata;
}


function get_recent_data(device_id) {

    console.log("http://pm25.iis.sinica.edu.tw/api/python3/get_recent_data?device_id=" + device_id)

    var rdata;
    $.ajax({
        type: "POST",
        url: "http://pm25.iis.sinica.edu.tw/api/python3/get_recent_data?device_id=" + device_id,
        async: false,
        dataType: "json",
        success: function (data) {
            rdata = data;
        }
    });

    console.log(rdata);
    return rdata;
}


function get_radius_data() {
    var rdata;

    if (source == "epa")
        furl = '../data/radius_data/epa.json'
    else
        furl = '../data/radius_data/airbox.json'
    $.ajax({
        type: "GET",
        //url: '../data/radius_data/' + source + '.json',
        url: furl,
        async: false,
        dataType: "json",
        success: function (data) {
            rdata = data;
            console.log(furl);
        }
    });

    console.log(rdata);
    return rdata;
}


function get_average_max_min_data(device_id, start_date, end_date, sample_rate, time_mode) {

    console.log("http://pm25.iis.sinica.edu.tw/api/python3/compute_average_max_min?device_id=" + device_id + "&start_date=" + start_date + "&end_date=" + end_date + "&sample_rate=" + sample_rate +
        "&time_mode=" + time_mode);

    var rdata;
    $.ajax({
        type: "POST",
        //url: "http://140.109.21.241/api/get_real_time_data_web?source=" + source,
        url: "http://pm25.iis.sinica.edu.tw/api/python3/compute_average_max_min?device_id=" + device_id + "&start_date=" + start_date + "&end_date=" + end_date + "&sample_rate=" + sample_rate +
        "&time_mode=" + time_mode,
        async: false,
        dataType: "json",
        success: function (data) {
            rdata = data;
            console.log("success!!");
        },
        error: function(xhr, status, error) {
            var err = eval("(" + xhr.responseText + ")");
            console.log(err.Message);
        }
    });

    console.log(rdata);
    return rdata;
}


function get_matrix_profile_data(device_id, start_date, end_date, sample_rate, query_length, distance_function, number_of_motifs, lower_limit_of_the_number_of_single_motif) {

    console.log("http://pm25.iis.sinica.edu.tw/api/python3/compute_matrix_profile?device_id=" + device_id + "&start_date=" + start_date + "&end_date=" + end_date + "&sample_rate=" + sample_rate +
        "&query_length=" + query_length + "&distance_function=" + distance_function + "&number_of_motifs=" + number_of_motifs + "&lower_limit_of_the_number_of_single_motif=" + lower_limit_of_the_number_of_single_motif);

    var rdata;
    $.ajax({
        type: "POST",
        //url: "http://140.109.21.241/api/get_real_time_data_web?source=" + source,
        url: "http://pm25.iis.sinica.edu.tw/api/python3/compute_matrix_profile?device_id=" + device_id + "&start_date=" + start_date + "&end_date=" + end_date + "&sample_rate=" + sample_rate +
        "&query_length=" + query_length + "&distance_function=" + distance_function + "&number_of_motifs=" + number_of_motifs + "&lower_limit_of_the_number_of_single_motif=" + lower_limit_of_the_number_of_single_motif,
        async: false,
        dataType: "json",
        success: function (data) {
            rdata = data;
            console.log("success!!");
        },
        error: function(xhr, status, error) {
            var err = eval("(" + xhr.responseText + ")");
            console.log(err.Message);
        }
    });

    console.log(rdata);
    return rdata;
}


/*
function getDeviceContribution(source) {
	var furl = "https://pm25-425e3.firebaseio.com/time/" + source + ".json";
	var rdata = {};
	$.ajax({
		url: furl,
		type: "GET",
		async: false,
		dataType: "json",
		success: function (data) {
			for (var records in data) {
				l2 = data[records];
				for (var id in l2) {
					if (id in rdata) {
						rdata[id] += l2[id];
					}
					else {
						rdata[id] = l2[id];
					}
				}
			}
		}
	});
  return rdata;
}
*/


function change_mode(){
	$("#mode").change(function(){
		clearInterval(now);
		var name = $("#mode").val();
		switch(name){
			case 'Profile':
				mode = "profile";
				get_data_and_show_on_the_map();
				now = setInterval(get_data_and_show_on_the_map,1000*300);
				break;
			case 'Radius':
				mode = "radius";
                get_data_and_show_on_the_map();
				now = setInterval(get_data_and_show_on_the_map,1000*300);
				break;
		}
		
	});	
}


function change_source(){
	$("#source").change(function(){
		clearInterval(now);
		var name = $("#source").val();
		switch(name){
			case 'ALL':
				source = "all";
				break;
			case 'Airbox':
				source = "airbox";
				break;
			case 'LASS':
				source = "lass";
				break;
			case 'EPA':
				source = "epa";
				break;
		}
		now = setInterval(get_data_and_show_on_the_map, 1000*300);
        get_data_and_show_on_the_map();
	});
}


function change_detail(){
	$("input[type=radio][name=select]").change(function(){
		clearInterval(now);
		console.log(this.value);

		switch(this.value){
			case 'timeseries':
				detail_chart_mode = "timeseries";
                document.getElementById("same").style.visibility = "hidden";
                document.getElementById("different_motif").style.visibility = "hidden";
                document.getElementById("different_average_max_min").style.visibility = "hidden";
                document.getElementById("go").style.visibility = "hidden";
                detail_chart(current_device_id);
				break;
            case 'average_max_min':
                detail_chart_mode = "average_max_min";
                document.getElementById("same").style.visibility = "visible";
                document.getElementById("different_motif").style.visibility = "hidden";
                document.getElementById("different_average_max_min").style.visibility = "visible";
                document.getElementById("go").style.visibility = "visible";
                detail_chart(current_device_id);
                break;
            case 'motif':
                detail_chart_mode = "motif";
                document.getElementById("same").style.visibility = "visible";
                document.getElementById("different_motif").style.visibility = "visible";
                document.getElementById("different_average_max_min").style.visibility = "hidden";
                document.getElementById("go").style.visibility = "visible";
                detail_chart(current_device_id);
				break;
		}
		now = setInterval(get_data_and_show_on_the_map, 1000*300);
	});
	
	$("#slider_tab_4").click(function(){

		//detail_chart is going show up
		if ($("#slider_scroll_4").css('bottom') == '-'+ 420 + 'px')
		{
			if (current_device_id != old_device_id)
			{
				console.log("need show detail chart");
				detail_chart(current_device_id);
			}
			
		}
        //detail_chart is going down
		else
		{
			old_device_id = current_device_id;
		}
	});
}


function input_parameter() {
	//startdate, enddate
	$("#startdate_input").datepicker({
		dateFormat: 'yy-mm-dd'
	}).datepicker('setDate', -7);
	
	$("#enddate_input").datepicker({
		dateFormat: 'yy-mm-dd'
	}).datepicker('setDate', -1);
	
	
	$("#startdate_input").change(function(){
		current_start_date = this.value;
	});
	
	$("#enddate_input").change(function(){
		current_end_date = this.value;
	});
	
	
	//set current_start_date, current_end_date
	var date = new Date();
	date.setDate(date.getDate() - 7); 
	var dd = date.getDate();
	var mm = date.getMonth() + 1; //January is 0!
	var yyyy = date.getFullYear();

	if (dd < 10) {
		dd = '0' + dd
	} 

	if (mm<10) {
		mm = '0' + mm
	}
	current_start_date = yyyy + '-' + mm + '-' + dd;
	
	var date = new Date();
	date.setDate(date.getDate() - 1); 
	var dd = date.getDate();
	var mm = date.getMonth() + 1; //January is 0!
	var yyyy = date.getFullYear();

	if (dd < 10) {
		dd = '0' + dd
	} 

	if (mm<10) {
		mm = '0' + mm
	}
	current_end_date = yyyy + '-' + mm + '-' + dd;
	
	
	//querylength
	$("#querylength_input").change(function(){
		var value = $("#querylength_input").val();
		switch(value){
			case '12':
				current_query_length = 12;
				break;
			case '24':
				current_query_length = 24;
				break;	
			case '36':
				current_query_length = 36;
				break;
			case '48':
				current_query_length = 48;
				break;
			case '60':
				current_query_length = 60;
				break;
			case '72':
				current_query_length = 72;
				break;
		}
	});
	
	//lowerlimitofthenumberofsinglemotif
	$("#lowerlimitofthenumberofsinglemotif_input").change(function(){
		var value = $("#lowerlimitofthenumberofsinglemotif_input").val();
		switch(value){
			case '2':
				current_lower_limit_of_the_number_of_single_motif = 2;
				break;
			case '3':
				current_lower_limit_of_the_number_of_single_motif = 3;
				break;	
			case '4':
				current_lower_limit_of_the_number_of_single_motif = 4;
				break;
			case '5':
				current_lower_limit_of_the_number_of_single_motif = 5;
				break;
			case '6':
				current_lower_limit_of_the_number_of_single_motif = 6;
				break;
		}
	});


    //timemode
    $("#timemode_input").change(function(){
        var value = $("#timemode_input").val();
        switch(value){
            case 'day':
                current_time_mode = "day";
                break;
            case 'hour':
                current_time_mode = "hour";
                break;
        }
    });
	
	//Go!
	$("#go").click(function(){
        compute = true;
		detail_chart(current_device_id);
	});
}


function get_data_and_show_on_the_map() {
	console.log("mode = " + mode + ", source = " + source);
	
	clear_map();

	
	if (mode == "profile") {

		var data = get_real_time_data();

        var level_color = ["#9EFF9E","#33FF00","#31D100","#FFFF00","#FFD000","#FF9900","#FF6666","#FF0000","#990000","#CE2EFF"];
        var level_value = [11,23,35,41,47,53,58,64,70,71];

		for (var source_name in data) {
			for (var index = 0; index < data[source_name].length; index++) {
				
				var lat = data[source_name][index].lat;
				var lon = data[source_name][index].lon;
				var device_id = data[source_name][index].device_id;
				var s_d0 = data[source_name][index].pm25;
				var s_h0 = data[source_name][index].humidity;
				var s_t0 = data[source_name][index].temperature;
				var name = data[source_name][index].name;
				var timestamp = data[source_name][index].timestamp;
				
				
				//console.log(index);
				
				
				
				pos2device[(parseFloat(lat),parseFloat(lon))] = device_id;
				
				device2name[device_id] = name;
				device2s_d0[device_id] = s_d0;
				device2s_t0[device_id] = s_t0;
				device2s_h0[device_id] = s_h0;
				
				if (parseFloat(lat) == 0.0)
					continue;
				
				//show on map
				var level = -1;
				if (parseInt(s_d0) >= level_value[9])
					level = 9;
				else {
					for (var i = 8; i >= 0; i--) {
						if (parseInt(s_d0) > level_value[i]){
							 level = i + 1;
							 break;
						}							
					}												
				}
				if (level == -1)
					level = 0;


				var popup = '<div >' + name + '</div>' +

							'<div class="quiet">' +  "PM25: " + s_d0.toString()+ "</br>" +
							"溫度: " + s_t0.toString()+ "</br>" +
							"濕度: " + s_h0.toString()+ "</div>" ;



						
				var popup_option = {
					'className' : 'popup',
					'closeButton' : false,
				}
				/*
				var marker = L.circle(
					[parseFloat(lat),parseFloat(lon)],
					300,
					{
						color: level_color[level],
						fillColor: level_color[level]
					}
				
				)
				.addTo(map)
				.bindPopup(popup,popup_option);
				*/


				// use circleMarker
				var marker = L.circleMarker(
					[parseFloat(lat),parseFloat(lon)],
					{
						radius: 20,
						color: level_color[level],
						fillColor: level_color[level]
					}
				
				)
				.addTo(map)
				.bindPopup(popup,popup_option);
				
				
				marker.on('click',function(e){
					//console.log(e);
					console.log(marker);
					e = e.target;
					id = pos2device[(e._latlng.lat,e._latlng.lng)];
					current_device_id = id;
					console.log(id);
					
					//detail chart is show up
					if ($("#slider_scroll_4").css('bottom') != '-'+ 420 + 'px')
						if (detail_chart_mode == "timeseries")
							detail_chart(id);
				});
			}
		}
	}

	else if (mode == "radius")	{
        console.log("YA");
        var data = get_radius_data();

        var level_color = ["#9EFF9E","#33FF00","#31D100","#FFFF00","#FFD000","#FF9900","#FF6666","#FF0000","#990000","#CE2EFF"];
        var level_value = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1];

        for (var source_name in data) {
            for (var index = 0; index < data[source_name].length; index++) {

                var lat = data[source_name][index].lat;
                var lon = data[source_name][index].lon;
                var device_id = data[source_name][index].device_id;
                var radius = data[source_name][index].Radius["04:00:00"];


				/*
                pos2device[(parseFloat(lat),parseFloat(lon))] = device_id;

                device2name[device_id] = name;
                device2s_d0[device_id] = s_d0;
                device2s_t0[device_id] = s_t0;
                device2s_h0[device_id] = s_h0;
				*/
                if (parseFloat(lat) == 0.0)
                    continue;

                //show on map
                var level = -1;
                if (parseFloat(radius) >= level_value[9])
                    level = 9;
                else {
                    for (var i = 8; i >= 0; i--) {
                        if (parseFloat(radius) > level_value[i]){
                            level = i + 1;
                            break;
                        }
                    }
                }
                if (level == -1)
                    level = 0;


                var popup = '<div >' + device_id + '</div>' +

                    '<div class="quiet">' +  "Radius: " + radius.toString() +
                    "</br>" +
                    "level: " + level.toString()+ "</br>" +"</div>" ;




                var popup_option = {
                    'className' : 'popup',
                    'closeButton' : false,
                }

				var marker = L.circle(
					[parseFloat(lat),parseFloat(lon)],
                    radius * 96 * 1000,
                    {
                        color: level_color[level],
                        fillColor: level_color[level]
                    }

				)
				.addTo(map)
				.bindPopup(popup,popup_option);


				/*
                // use circleMarker
                var marker = L.circleMarker(
                    [parseFloat(lat),parseFloat(lon)],
                    {
                        radius: 20,
                        color: level_color[level],
                        fillColor: level_color[level]
                    }

                )
                    .addTo(map)
                    .bindPopup(popup,popup_option);
				*/
				/*
                marker.on('click',function(e){
                    //console.log(e);
                    console.log(marker);
                    e = e.target;
                    id = pos2device[(e._latlng.lat,e._latlng.lng)];
                    current_device_id = id;
                    console.log(id);

                    //detail chart is show up
                    if ($("#slider_scroll_4").css('bottom') != '-'+ 420 + 'px')
                        if (detail_chart_mode == "timeseries")
                            detail_chart(id);
                });*/
            }
        }
	}
	console.log("get_data_and_show_on_the_map : DONE!!");
	
}



function main(){
	
	// initial the map
	initial_map();

	// get the data and show on the map
	get_data_and_show_on_the_map();

	// every 300 seconds it will re-execute get_data_and_show_on_the_map
	now = setInterval(get_data_and_show_on_the_map,1000*300);

	// event listener
	change_mode();
	change_source();
	change_detail();
	input_parameter();
}



main();