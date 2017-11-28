/* manager */ 
#include "RemoteForceInterface.h"
#include "Global.h"

RemoteForceInterface::RemoteForceInterface() : workers(0), masters(0), intercomm(MPI_COMM_NULL), totsize(0) {
   int *universe_sizep, flag;
   world_size = MPMD.world_size;
   universe_size = MPMD.universe_size;
}

RemoteForceInterface::~RemoteForceInterface() {
  if (intercomm != MPI_COMM_NULL) {
    MPI_Comm_free(&intercomm);
  }
}

int RemoteForceInterface::Start(char * worker_program, char * args[]) {
   if (intercomm != MPI_COMM_NULL) {
    error("RemoteForceInterface(M) Already started\n");
    return -2;
   }
   if (universe_size == world_size) {
    ERROR("No room to start workers"); 
    return -1;
   }
   MPMDIntercomm inter = MPMD["ESYSPARTICLE"];
   if (! inter) {
    printf("Spawning ...\n");
    inter = MPMD.Spawn(worker_program, args, universe_size - world_size,MPI_INFO_NULL);
   }
   intercomm = inter.work;
   
   
   MPI_Comm_remote_size(intercomm, &workers);
   MPI_Comm_size(intercomm, &masters);
   MPI_Comm_rank(intercomm, &rank);
   sizes.resize(workers, 0);
   offsets.resize(workers+1, 0);
   reqs.resize(workers);
   stats.resize(workers);
   return 0;
}

void RemoteForceInterface::Close() {
  if (intercomm == MPI_COMM_NULL) return;
  output("RemoteForceInterface(M) Closing ...\n");
  totsize = 0;
  for (int i=0; i<workers; i++) {
   sizes[i] = 0;
   offsets[i] = 0;
  }
  MPI_Comm_free(&intercomm);
  intercomm = MPI_COMM_NULL;
}


void RemoteForceInterface::GetParticles() {
    if (intercomm == MPI_COMM_NULL) return;
    debug1("RemoteForceInterface(M) Exchange of sizes ...\n");
    MPI_Alltoall(NULL, 0, MPI_RFI_SIZE_T, &sizes[0], 1, MPI_RFI_SIZE_T, intercomm);
    for (int i=0; i<workers; i++) if (sizes[i] == RFI_FINISHED) { Close(); return; }
    for (int i=0; i<workers; i++) debug1("RemoteForceInterface(M) [%2d] we got %ld from %d\n", rank, (size_t) sizes[i], i);
    for (int i=0; i<workers; i++) offsets[i+1] = offsets[i] + sizes[i];
    totsize = offsets[workers];
    if (totsize > tab.size()) tab.resize(totsize);
    debug1("RemoteForceInterface(M) Sending ...\n");
    for (int i=0; i<workers; i++) {
        MPI_Irecv(&tab[offsets[i]], sizes[i], MPI_RFI_REAL_T, i, i, intercomm, &reqs[i]);
    }
    MPI_Waitall(workers, &reqs[0], &stats[0]);
}

void RemoteForceInterface::SetParticles() {
    if (intercomm == MPI_COMM_NULL) return;
    debug1("RemoteForceInterface(M) Receiving ...\n");
    for (int i=0; i<workers; i++) {
        MPI_Isend(&tab[offsets[i]], sizes[i], MPI_RFI_REAL_T, i, i+workers, intercomm, &reqs[i]);
    }
    MPI_Waitall(workers, &reqs[0], &stats[0]);
}
