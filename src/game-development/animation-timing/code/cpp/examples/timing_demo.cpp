#include "animation.hpp"
#include <iomanip>
#include <iostream>
int main() {
  anim::FrameRate rate{24,1};
  std::cout << "frame,time_seconds,eased_x\n";
  for (int frame=0;frame<60;++frame) {
    const double t=rate.time_at(frame);
    std::cout<<frame<<','<<std::fixed<<std::setprecision(6)<<t<<','
             <<(320.0*anim::smoothstep(t/2.5))<<'\n';
  }
}
