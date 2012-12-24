<?php

#подключаем API
require_once 'phpFlickr/phpFlickr.php';

#апи и секретный ключ генерится в аккаунте, token получаем после авторизации на свой скрипт, ну и имя вашего аккаунта
$api    	= '';
$secret 	= '';
$token		= '';
$username	= '';

#логинимся
$f = new phpFlickr($api, $secret, false);
$f->setToken($token);

#файлы с кэшами, в базу писать нет смысла потому все храним в файлах
$cache_file		= dirname(__FILE__).'/cache.txt';
$cache 			= unserialize(file_get_contents($cache_file));

$gcache_file	= dirname(__FILE__).'/group_cache.txt';
$gcache 		= unserialize(file_get_contents($gcache_file));

#самый главный массив, прописываем какие теги в какие группы закидываем, само собой мы должны быть в этих группах
$tags = array(
	'steet' 		=> '94761711@N00|97329809@N00|355036@N23|319155@N20|25351450@N00',
	'bw'			=> '16978849@N00|61859776@N00|91479755@N00|405546@N20',
	'landscape'		=> '23854677@N00|453397@N24|40969270@N00|549178@N24|27303736@N00|1003995@N21|563268@N25',
	'night'			=> '11947580@N00|52240105042@N01|66063005@N00|35489622@N00',
	'sunset'		=> '52242317293@N01|80264197@N00|51649914@N00|11947580@N00|52240105042@N01|66063005@N00|35489622@N00|563268@N25',
	'sunrise'		=> '52242317293@N01|80264197@N00|51649914@N00|11947580@N00|52240105042@N01|66063005@N00|35489622@N00|563268@N25',
	'beach'			=> '81682017@N00|52240744699@N01|60658532@N00',
	
	'snowboard'		=> '52241372332@N01|96821971@N00|607062@N20',
	'color'			=> '71332142@N00|28747776@N00',
	'flower'		=> '13378274@N00|741558@N22',
	'person'		=> '70823775@N00|58146428@N00',
	'animal'		=> '47643757@N00|35025468@N00|741558@N22',
	'urban'			=> '64262537@N00|453397@N24|52241627890@N01',
	'long exposure'	=> '52240257802@N01|38514992@N00|11947580@N00|52240105042@N01|66063005@N00|35489622@N00',
	'nature'		=> '65248419@N00|741558@N22|91806330@N00',
	'children'		=> '38517647@N00',
	'sky'			=> '89594630@N00|27208839@N00|73183316@N00|59171336@N00',
	'reflection'	=> '52240405789@N01|77371384@N00',
	'red'			=> '73929910@N00',
	'clouds'		=> '73183316@N00|59171336@N00|27208839@N00',
	'shadows'		=> '52447432@N00|52241084581@N01',
	'winter'		=> '52239922490@N01',
	'mountain'		=> '62119907@N00',
	'waterwall'		=> '21637543@N00',
	
	//группа куда попадают все фотографии
	'all'			=> '34427469792@N01|1577604@N20|38436807@N00|11252682@N00|347276@N23|66652279@N00|41425956@N00|20759249@N00|1902869@N24|58898522@N00|52240293230@N01|76535076@N00|95309787@N00|1148171@N20|715137@N23|11488522@N00|402895@N25|1069543@N21|1054821@N23',
	
	'finland'		=> '52240607517@N01',
	'germany'		=> '51035715323@N01|70543216@N00|300478@N25|38549162@N00|52559897@N00',
	'greece'		=> '44124303046@N01|11681106@N00',	
	'italy'			=> '31746602@N00|37996580003@N01|37996580003@N01|52240278816@N01',
	'thailand'		=> '52242280377@N01|52242376463@N01',
	'singapore'		=> '44124328512@N01|52242383417@N01|82009867@N00',
	'indonesia'		=> '746103@N25',
	'bali'			=> '52242383744@N01|666749@N24|50913842@N00',
	'europe'		=> '1286471@N20|',
	'east europe'	=> '18362947@N00|66465160@N00',
	'austria'		=> '62583794@N00',
	'hungary'		=> '488293@N25',
	'croatia'		=> '12855550@N00',
	'slovania'		=> '31849566@N00',
	'bangkok'		=> '74136425@N00',
	'cambodia'		=> '52242386617@N01',
	'vietnam'		=> '52242385927@N01|1130282@N20|44124468667@N01',
	'toskana'		=> '20168080@N00',	

	// D. Monastyrskiy flikrpwd: AkbrhAjhtdf

	'flowers'		=> '13378274@N00|34778850@N00|36799380@N00|50719875@N00|527093@N21|611299@N22|376011@N22|98634088@N00',
	'close-up'		=> '52241335207@N01|95174098@N00',
	'natures'		=> '40969270@N00|92206151@N00|65248419@N00|366552@N23|496080@N22|340677@N23|728852@N24|892535@N20|17044869@N00|91806330@N00|386378@N21',
	'macro'			=> '49503086607@N01|21563296@N00|608399@N24',
	'insects'		=> '41324459@N00|33818533@N00',
	'bokeh'			=> '445664@N23|88081697@N00',
	'waterdrops'	=> '41978077@N00',
	'mountains'		=> '41425956@N00|',
	'landscapes'	=> '23854677@N00|78249294@N00|549178@N24|13197975@N00',
	'mushrooms'		=> ''

);

#мой аккаунт
$me 		= $f->people_findByUsername($username);
$photos_url = $f->urls_getUserPhotos($me['id']);

#если кэш с группой пустой, то создадим его. процесс довольно долгий, потому и сделал кэш
if ( empty($gcache) ) {
	$groups 	= $f->people_getPublicGroups( $me['id'] );
	foreach ( $groups as $k=>$group ) {
		$get 			= $f->groups_getInfo( $group['nsid'] );
		$groups[$k] 	= $get['group'];
	}
	
	$f = fopen($gcache_file, 'w');
	fputs($f, serialize($groups));
	fclose($f);
} else {
	$groups = $gcache;
}

#запишем в кэш в какой группе какие картинки ну и в лог выведем это все
foreach ( $groups as $k=>$v ) {
	$photos = $f->groups_pools_getPhotos( $v['id'], NULL, $me['id'] );
	
	$cache[$v['id']]['ids'] = array();
	foreach ( $photos['photos']['photo'] as $kk=>$photo ) {
		$cache[$v['id']]['ids'][] = $photo['id'];
	}
	
	echo date('m/d/Y H:i')." ".$v['name'].": ".count($cache[$v['id']]['ids'])."\n";
}

$group_data = array();

#во всех группах есть лимиты на добавление, потому проверим куда можем писать куда нет и ограничим кол-во картинок
foreach ( $groups as $k=>$group ) {
	$check 					= $group['throttle'];
	$groups[$k]['limit'] 	= 0;
  
	$last 	= !empty($cache[$group['id']]['last']) ? $cache[$group['id']]['last'] : 0;
  
	if ( $check['mode'] == 'none' ) {
		$groups[$k]['limit'] = 2;
	} elseif ( $check['mode'] == 'day' ) {
		$limit 	= 24*3600;
		
		if ( $last + $limit <= time() ) {
			$groups[$k]['limit'] = $check['count'];
		}
	} elseif ( $check['mode'] == 'week' ) {
		//check cache
		$limit 	= 24*3600*7/$check['count'];
	
		if ( $last + $limit <= time() ) {
			$groups[$k]['limit'] = 1;  
		}
	} elseif ( $check['mode'] == 'month' ) {
		//check cache
		$limit 	= 24*3600*30/$check['count'];
	
		if ( $last + $limit <= time() ) {
			$groups[$k]['limit'] = 1;  
		}	
	}
	
	//спамить группы без лимитов нет смысла, потому максимум добавляем 2 фото за раз.
	if ( $groups[$k]['limit'] > 2 ) {
		$groups[$k]['limit'] = 2;
	}
	
	$group_data[$group['id']] = $groups[$k];
}

//выберем все фото и склеим их, склеиваем потому что у меня больше 500 фотографий
$photos1 = $f->people_getPublicPhotos( $me['id'], NULL, "tags", 500, 0 );
$photos2 = $f->people_getPublicPhotos( $me['id'], NULL, "tags", 500, 2 );

$p = array();
foreach ((array)$photos1['photos']['photo'] as $photo) {
	$p[] = $photo;	
}
	
foreach ((array)$photos2['photos']['photo'] as $photo) {
	$p[] = $photo;	
}

//отсортируем в обратном порядке
$p = array_reverse($p);

foreach ( $p as $photo) {
	
	//обработаем теги
	foreach ( explode(" ", $photo['tags']) as $k=>$tag ) {
		if ( !empty($tags[$tag]) ) {
			foreach ( explode("|", $tags[$tag]) as $key=>$gid ) {
				if ( !empty($group_data[$gid]['limit']) && ( empty($cache[$gid]) || empty($cache[$gid]['ids']) || !in_array($photo['id'], $cache[$gid]['ids']) ) ) {
					
					echo date('m/d/Y H:i')." Фото: ".$photo['id']." Тег: ".$tag." Группа: ".$group_data[$gid]['name']." ".$gid." Лимит: ".$group_data[$gid]['limit']." Результат: ";	
				
					#добавление в pool группы
					$x = $f->groups_pools_add( $photo['id'], $gid );
					
					#запомним дату и уменьшим лимит
					$group_data[$gid]['limit']--;
					$cache[$gid]['last']	= time();
					
					echo ( !empty($x) ? 'успешно' : 'не успешно '.$f->error_code." ".$f->error_msg )."\n";
				}
			}
		}
	}
	
	//обработаем общую группу all
	foreach ( explode("|", $tags['all']) as $key=>$gid ) {
		if ( !empty($group_data[$gid]['limit']) && ( empty($cache[$gid]) || empty($cache[$gid]['ids']) || !in_array($photo['id'], $cache[$gid]['ids']) ) ) {

			echo date('m/d/Y H:i')." Фото: ".$photo['id']." Тег: ".$tag." Группа: ".$group_data[$gid]['name']." ".$gid." Лимит: ".$group_data[$gid]['limit']." Результат: ";	
			
			#добавление в pool группы
			$x = $f->groups_pools_add( $photo['id'], $gid );
				
			#запомним дату и уменьшим лимит
			$group_data[$gid]['limit']--;
			$cache[$gid]['last']	= time();
				
			echo (!empty($x) ? 'успешно' : 'не успешно '.$f->error_code." ".$f->error_msg)."\n";
		}
	}
}

#сохраним кэш
$f = fopen($cache_file, 'w');
fputs($f, serialize($cache));
fclose($f);

?>