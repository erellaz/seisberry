//Geophone support RTC 10Hz

//Dimensions-------------------------------------------------
//All in mm

// Geophone dimensions
hg=34;   //height
dg=26.5;  //diameter 

// support
bases=50;
hs=7;
w=9;
e=5;

//holes
dh=3;
th=27;

//groove
gw=6;
gd=5;
gdd=3;
//--------------------------------------------------------------
$fn=100;//resolution

module Make_body() {
difference(){
union(){
translate([0,0,hs/2]) cube([bases,bases,hs],center=true);
translate([0,0,hg/4]) cylinder(h=hg/2,d=dg+9,center=true);
}
translate([0,0,e+hg/2]) cylinder(h=hg,d=dg,center=true);
}
}
module Make_holes() {
union(){
rotate([0,0,45])translate([th,0,0]) cylinder(h=3*hs,d=dh,center=true);
rotate([0,0,135])translate([th,0,0]) cylinder(h=3*hs,d=dh,center=true);
rotate([0,0,225])translate([th,0,0]) cylinder(h=3*hs,d=dh,center=true);
rotate([0,0,315])translate([th,0,0]) cylinder(h=3*hs,d=dh,center=true);
}}

module Make_groove() {
    union(){
    cube([100,gw,gd],center=true);
    //rotate([0,0,90]) cube([100,gw,gd],center=true);
}}

module Make_groove_holes(){
   union(){
    translate([(gdd+bases)/2-7.5,0,0])rotate([0,90,0])cube([100,gw,gdd],center=true);
    translate([-(gdd+bases)/2+7.5,0,0])rotate([0,90,0])cube([100,gw,gdd],center=true);
}}


difference(){
difference(){
difference(){
Make_body();
Make_holes();
}
Make_groove();
}
Make_groove_holes();
}

/*
color( "green", 1.0 ) {
translate([0,0,e+hg/2]) cylinder(h=hg,d=dg,center=true);
}
*/