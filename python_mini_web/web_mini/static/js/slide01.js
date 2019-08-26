$(function(){

	// 获取所有li标签
	var $li = $('.slide_list li')
	
	// 设置除第一个li标签，其他设置left:760
	//$li.not(':first').css({'left':760})
	$li.eq(0).css({'left':0}).siblings().css({'left':760})  // 和上面的效果相同

	// 获取li标签的个数
	var $len = $li.length;

	// 要运动过来的页面的索引值
	var nowli = 0;
	// 要离开的页面的索引值
	var prevli = 0;

	// 获取到两个左右按钮
	var $prev = $('.prev')
	var $next = $('.next')

	// 获取小黑点的ul标签
	var $point_con = $('.points')

	// 定时器初始化
	var timer = null;

	// 设置开关
	var ismove = false;

	// 获取幻灯片页面的ul元素
	var $slide = $('.slide')

	// 通过循环，进行小黑点元素的内部添加
	for(i=0;i<$len;i++){

		// 创建空的li标签
		var $newli = $('<li>')

		if(i==0){
			// 给第一个li标签添加样式
			$newli.addClass('active');
		}

		$point_con.append($newli)
	}


	var $points = $('.points li')
	// 设置小黑点的点击事件
	$points.click(function(){

		// 获取被点击的小黑点的索引值
		nowli = $(this).index();

		// 消除多次点击自己出现的bug
		if(nowli==prevli){
			return;
		}

		// 设置点击时，点的样式
		$(this).addClass('active').siblings().removeClass('active')
		// 调用函数
		move();
	})

	//点击向前的按钮切换幻灯片
	$prev.click(function(){
		if(ismove){
			return;
		}
		ismove = true;
		nowli--;
		move();
	// 注意：设置画面移动时下方黑点变化的样式
	$points.eq(nowli).addClass('active').siblings().removeClass('active')	
	})

	$next.click(function(){
		if(ismove){
			return;
		}
		ismove = true;
		nowli++;
		move();
		// 注意：不要将此条语句放到move函数的上面，因为move函数会改变nowli的值
		$points.eq(nowli).addClass('active').siblings().removeClass('active')	
	})

	// 设置定时器   
	timer = setInterval(autoplay,3000)

	// 设置鼠标放上去的效果   和类似于css中的hover,这是属于jquery独特的鼠标效果
	$slide.mouseenter(function(){
		clearInterval(timer);
	})

	// 设置鼠标离开时的效果
	$slide.mouseleave(function(){
		timer = setInterval(autoplay,3000)
	})

	// 设置自动播放函数
	function autoplay(){
		// 设置默认向左滚动页面的效果
		nowli++;
		move();
		// 注意：不要将此条语句放到move函数的上面，因为move函数会改变nowli的值
		$points.eq(nowli).addClass('active').siblings().removeClass('active')
	}

	// 设置页面移动函数
	function move(){

		// 针对于第一张页面，当触发<按钮时
		if(nowli<0){
			// 设置即将要进入页面的索引值
			nowli = $len-1;
			// 设置即将要离开的页面的索引值
			prevli = 0;

			// 设置即将进入的页面的初始位置
			$li.eq(nowli).css({'left':-760});

			// 设置页面的进入动画
			$li.eq(nowli).animate({'left':0});

			// 设置离开页面的动画
			$li.eq(prevli).animate({'left':760},function(){
				ismove = false;
			});

			prevli = nowli;
			// 当前条件为特例，不能执行下面的条件
			return;


		}
		// 针对于最后一张页面，当触发>按钮时
		if(nowli>$len-1)
		{
			nowli = 0;
			prevli = $len-1;

			$li.eq(nowli).css({'left':760});

			$li.eq(nowli).animate({'left':0});

			$li.eq(prevli).animate({'left':-760},function(){
				ismove = false;
			});

			prevli = nowli;
			// 当前条件为特例，不能执行下面的条件
			return;
		}


		// 类似于在指定范围内点击>的效果
		if (nowli>prevli){
			// 设置即将出现的页面在当前页面的右面
			$li.eq(nowli).css({'left':760});
			// 设置移入动画
			$li.eq(nowli).animate({'left':0});
			// 设置移出动画
			$li.eq(prevli).animate({'left':-760},function(){
				ismove = false;
			});
			// 将刚才移进来的页面设置下一次要离开的页面
			prevli = nowli;
		}
		// 类似于在指定范围内点击<的效果
		else{
			// 设置即将出现的页面在当前页面的左面
			$li.eq(nowli).css({'left':-760});
			$li.eq(nowli).animate({'left':0});
			$li.eq(prevli).animate({'left':760},function(){
				ismove = false;
			});
			prevli = nowli;
		}
	}

})