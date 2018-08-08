R=30;
D=60;
translate([R,0,R]) {
    sphere(d=R*2);
    for (x=[1:4]) {
        translate([0,x*D,0]) {
            sphere(d=R*2);
        }
    }
    rotate([-90,0,0]) cylinder(h=8*R,r1=R,r2=R/2);
    rotate([90,0,0]) cylinder(h=3*R,r1=R,r2=R);
    translate([0,4*D,0]) rotate([-90,0,0]) cylinder(h=3*R,r1=R,r2=R);
}