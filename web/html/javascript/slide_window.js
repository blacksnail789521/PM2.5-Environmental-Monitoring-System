
function set_view(){

	/* change point slider */ 
	$(function(){

		$("#slider_tab_1").click(function(){
			if ($("#slider_scroll_1").css('top') == '-'+ 290 + 'px')
			{
				$("#slider_scroll_1").animate({ top:'0px' }, 600 ,'swing');
			}
		});
		
	/*	
		$("#slider_scroll_1").mouseleave(function(){
			$("#slider_scroll_1").animate( { top:'-'+290 }, 600 ,'swing');	
		});
	*/

		$("#map").click(function(){
			$("#slider_scroll_1").animate( { top:'-'+290 }, 600 ,'swing');	
			console.log('map click event!');
		});


	});


	/* motif slider */
	$(function(){

		$("#slider_tab_2").click(function(){
			if ($("#slider_scroll_2").css('top') == '-'+ 290 + 'px')
			{
				$("#slider_scroll_2").animate({ top:'0px' }, 600 ,'swing');
			}
		});
		
	/*	
		$("#slider_scroll_2").mouseleave(function(){
			$("#slider_scroll_2").animate( { top:'-'+290 }, 600 ,'swing');	
		});
	*/
		$("#map").click(function(){
			$("#slider_scroll_2").animate( { top:'-'+290 }, 600 ,'swing');		
		});

	});


	/* outbreak slider */
	$(function(){

		$("#slider_tab_3").click(function(){
			if ($("#slider_scroll_3").css('top') == '-'+ 290 + 'px')
			{
				$("#slider_scroll_3").animate({ top:'0px' }, 600 ,'swing');
			}
		});
		
	/*	
		$("#slider_scroll_3").mouseleave(function(){
			$("#slider_scroll_3").animate( { top:'-'+290 }, 600 ,'swing');	
		});
	*/

		$("#map").click(function(){
			$("#slider_scroll_3").animate( { top:'-'+290 }, 600 ,'swing');	
		});

	});


	/* 詳細資訊 slider */
	$(function(){

		$("#slider_tab_4").click(function(){
			if ($("#slider_scroll_4").css('bottom') == '-'+ 420 + 'px')
			{
				//console.log("up");
				$("#slider_scroll_4").animate({ bottom:'0px' }, 600 ,'swing');
			}
			else {
				//console.log("down");
				$("#slider_scroll_4").animate( { bottom:'-'+420 }, 600 , 'swing' );
			}
		});
		
	/*	
		$("#slider_scroll_4").mouseleave(function(){
			$("#slider_scroll_4").animate( { bottom:'-'+420 }, 600 ,'swing');	
		});	
	*/


		
			

		
	});


	/* 指標 slider */
	$(function(){

		$("#slider_tab_5").click(function(){
			if ($("#slider_scroll_5").css('bottom') == '-'+ 420 + 'px')
			{
				//console.log("up");
				$("#slider_scroll_5").animate({ bottom:'0px' }, 600 ,'swing');
			}
			else{
				//console.log("down");
				$("#slider_scroll_5").animate( { bottom:'-'+420 }, 600 , 'swing' );
			}
		});
		
	/*	
		$("#slider_scroll_4").mouseleave(function(){
			$("#slider_scroll_4").animate( { bottom:'-'+420 }, 600 ,'swing');	
		});	
	*/

		
			

		
	});


	$(function(){
		var width = $("#level_information").width();
		
		width = width +185;
		
		var adjust = -width/2;

		
		$("#level_information").css("left"," 50%");
		$("#level_information").css("margin-left",adjust+"px");
	});

}

set_view();
$(window).resize(set_view);






