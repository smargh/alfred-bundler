<?php


set_error_handler('myErrorHandler');
register_shutdown_function('fatalErrorShutdownHandler');

function myErrorHandler($code, $message, $file, $line) {
 echo "Fatal Error: $code : $message $file $line";
}

function fatalErrorShutdownHandler()
{
  $last_error = error_get_last();
  if ($last_error['type'] === E_ERROR) {
    // fatal error
    myErrorHandler(E_ERROR, $last_error['message'], $last_error['file'], $last_error['line']);
  }
}


// Set to use head for tests
$_ENV['AB_BRANCH']                  = 'devel';
$_ENV['AB_TESTING']                 = TRUE;

$_ENV[ 'alfred_theme_background' ]  = 'rgba(255,255,255,0.98)';
$_ENV[ 'alfred_workflow_bundleid' ] = 'com.bundler.testing.poop';
$_ENV[ 'alfred_workflow_name' ]     = 'PHP BUNDLER TESTING FRAMEWORK';

require_once( 'alfred.bundler.php' );

$b = new AlfredBundler;
$i = new AlfredBundlerIcon( $b );

$major = $b->major_version;
$fallback = $_SERVER['HOME'] . "/Library/Application Support/Alfred 2/Workflow Data/alfred.bundler-{$major}/bundler/meta/icons/default";

$tests[] = 'env_bundle_test';
// $tests[] = 'normalize_color_test';
// $tests[] = 'color_tests';
// $tests[] = 'color_inverse_test';
// $tests[] = 'color_alter_test';
// $tests[] = 'normalize_3_hex';
// $tests[] = 'normalize_3_hex_caps';
// $tests[] = 'download_icon';
// $tests[] = 'download_bad_icon_url';
// $tests[] = 'get_system_icon';
// $tests[] = 'get_bad_system_icon';
$tests[] = 'install_bundler_test';


// This test will ultimately fail because it will delete the bundler directory,
// then it will reinstall itself, and then, it will redeclare the class...
function install_bundler_test() {
  global $b;
  $b->rrmdir( $b->data );
  $c = new AlfredBundler;
  echo $c->data;
  return TRUE;
}

function get_bad_system_icon() {
  global $b, $fallback;
  $icon = $b->icon( 'system', 'Accoufdasdfasnts' );
  if ( file_exists( $icon ) && $icon == $fallback . '.icns' )
    return TRUE;
  else
    return FALSE;
}


function get_system_icon() {
  global $b, $fallback;
  $icon = $b->icon( 'system', 'Accounts' );
  if ( file_exists( $icon ) )
    return TRUE;
  else
    return FALSE;
}


function download_icon() {
  global $b;
  $icon = $b->icon( 'elusive', 'dashboard', 'ab3' );
  if ( $icon == $_SERVER['HOME'] . "/Library/Application Support/Alfred 2/Workflow Data/alfred.bundler-devel/data/assets/icons/elusive/aabb33/dashboard.png")
    return TRUE;
  else {
    return FALSE;
  }

}

// checks to make sure the fallback is sent rather than anything else
function download_bad_icon_url() {
  global $b, $fallback;
  $icon = $b->icon( 'elusive', 'dashssboard', 'ab3' );
  if ( $icon == $fallback . '.png')
    return TRUE;
  else {
    echo $icon;
    return FALSE;
  }

}

function normalize_3_hex_caps() {
  global $i;
  $color = strtoupper( generate_hex( FALSE ) );
  $color2 = $i->color( $color );

  $answer = '';
  for ($x=0; $x<3; $x++ ) :
    $answer .= $color[$x] . $color[$x];
  endfor;
  $answer = strtolower( $answer );

  if ( $answer == $color2 )
    return TRUE;
  else
    return FALSE;

}

function normalize_3_hex() {
  global $i;

  $color = generate_hex( FALSE );
  $color2 = $i->color( $color );

  $answer = '';
  for ($x=0; $x<3; $x++ ) :
    $answer .= $color[$x] . $color[$x];
  endfor;
  if ( $color2 == $answer )
    return TRUE;
  else
    return FALSE;
}

// For iterative color inverse tests... passing 100% on 100k checks.
// $failed = 0;
// $passed = 0;
// $number = 1000;
// $start = microtime();
// for ( $x=0; $x<$number; $x++ ) :
//
//   echo "Calling color inverse test " . ($x + 1) . ": ";
//   if ( color_inverse_test() ) {
//     $passed++;
//   } else {
//     $failed++;
//   }
//
// endfor;
// echo "======================================================" . PHP_EOL;
// echo "Completed $number tests in " . round(((microtime() - $start) / 1000000), 3) . " seconds.";
// echo "For 100000 tests, we passed $passed (" . ($passed/$number)*100 . "%)" . PHP_EOL;
//
// die();
function color_inverse_test() {
  global $i;

  $color = generate_hex();
  $hex1 = $i->color( $color );
  $rgb1 = $i->hexToRgb( $hex1 );
  $hsv  = $i->rgbToHsv( $rgb1 );
  $rgb2 = $i->hsvToRgb( $hsv );
  $hex2 = $i->rgbToHex($rgb2);
  if ( $hex1 == $hex2 ) {
    // echo "$hex1 == $hex2" . PHP_EOL;
    return TRUE;
  }
  else {
    // echo PHP_EOL;
    // echo "     * Debug for " . __FUNCTION__ . ':  ';
    echo "$hex1 != $hex2" . PHP_EOL;
    // print_r( $color ); echo PHP_EOL;
    // print_r( $rgb1 ); echo PHP_EOL;
    // print_r( $hsv ); echo PHP_EOL;
    // print_r( $rgb2 ); echo PHP_EOL;
    // print_r( $hex2 ); echo PHP_EOL;
    return FALSE;
  }


}

function color_alter_test() {
  global $i;
  $color = generate_hex();
  $altered = $i->alter( $color );
  if ( $color == $altered )
    return FALSE;
  else
    return TRUE;
  // echo "$color : $altered" . PHP_EOL;
  // We need to verify that this is good and plays within color spaces correctly.
}

function color_tests() {
  global $b, $i;

  $color = generate_hex();
  if ( $color == $i->color( $color ) )
    return TRUE;
  else
    return FALSE;

}


function generate_hex( $full = TRUE ) {
  if ( $full )
    $n = 6;
  else
    $n = 3;
  $hex = '';
  for( $i=0; $i<$n; $i++) {
    $hex .= get_hex();
  }
  return $hex;
}

function get_hex( ) {
  $hex = array_merge( range( 'a', 'f' ), range( 0, 9 ) );
  return $hex[ mt_rand( 0, 15 ) ];
}

function normalize_color_test() {
  global $b, $i;

  $color = $i->color( '000' );
  if ( $i->color( '000' ) == '000000' )
    return TRUE;

  return FALSE;
}

// Test, let's formalize these later.
function env_bundle_test() {
  global $b;

  if ( $b->bundle() == $_ENV[ 'alfred_workflow_bundleid' ] )
    return TRUE;
  else
    return FALSE;

}

// Run all tests
function run_tests( $tests ) {

$count = 1;
$total = count( $tests );
$passed = 0;
$failed = 0;
echo PHP_EOL;
echo "Starting Tests...." . PHP_EOL;
echo "======================================================" . PHP_EOL;
  foreach( $tests as $test ) {
    echo "({$count}/{$total}) Calling {$test} test... ";
    $result = call_user_func( $test );
    if ( $result == TRUE ) {
      echo " ...passed." . PHP_EOL;
      $passed++;
    } else {
      echo " ...failed." . PHP_EOL;
      $failed++;
    }
    $count++;
  }
echo "------------------------------------------------------" . PHP_EOL;
echo "Passed $passed of $total tests (" . ($passed/$total * 100) . "%)." . PHP_EOL;
echo "Failed $failed of $total tests (" . ($failed/$total * 100) . "%)." . PHP_EOL;

}

run_tests( $tests );
