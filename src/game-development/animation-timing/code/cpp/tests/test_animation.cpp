#include "animation.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
int main() {
  using namespace anim;
  assert(std::abs(FrameRate{24000,1001}.time_at(24000)-1001.0)<1e-9);
  assert(std::abs(smoothstep(0.5)-0.5)<1e-12);
  validate_exposures(5, {{"A",0,2},{"B",2,2},{"C",4,1}});
  bool caught=false;
  try { validate_exposures(4, {{"A",0,2},{"B",3,1}}); }
  catch(const std::invalid_argument&) { caught=true; }
  assert(caught);
  Body b{0,0,2}; b.advance(0.1,10);
  assert(std::abs(b.velocity-0.5)<1e-12);
  Spring spring{1,0,0,7,0.7};
  for(int i=0;i<120;++i) spring.step(1.0/120);
  assert(std::abs(spring.position)<0.1);
  FixedStep clock{0.01}; int n=0;
  assert(clock.advance(0.025,[&](double dt){assert(dt==0.01);++n;})==2);
  assert(n==2 && std::abs(clock.alpha()-0.5)<1e-9);
  std::cout << "animation_cpp_tests: PASS\n";
}
