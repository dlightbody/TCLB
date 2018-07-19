CudaDeviceFunction float2 Color() {
  float2 ret;
  ret.x = 0;
  ret.y = 1;
  return ret;
}

CudaDeviceFunction void Init() { }

CudaDeviceFunction void Run() { }

CudaDeviceFunction void Init() {
  u = ;
  v = 0;
}

CudaDeviceFunction void Run() {
  u = u(0,0);
  v = v(0,0);
}

CudaDeviceFunction real_t getU() {
  return u(0,0);
}

CudaDeviceFunction float2 Color() {
  float2 ret;
  ret.x = getU();
  ret.y = 1;
  return ret;
}

CudaDeviceFunction void Init() {
  u = Value;
  v = 0;
}


