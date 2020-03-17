#include <iostream>
#include <map>
#include <set>
#include <vector>

int solveC(int* conflits_list, int nb_conflits,int* res_list)
{
  std::cout<<"SOLVE CONFLITS"<<nb_conflits<<std::endl;
  std::set<int> labels_set ;
  std::map<int,std::vector<int> > label_conflits ;
  std::vector<int> labels ;
  std::size_t c_index = 0 ;
  for(int i=0;i<nb_conflits;++i)
  {
     int c0 = conflits_list[2*i] ;
     {
         auto iter = labels_set.insert(c0) ;
         //std::cout<<"C[0]"<<c0<<" "<<iter.second<<std::endl ;
         if(iter.second)
         {  
             labels.push_back(c0) ;
         }
     }
     label_conflits[c0].push_back(c_index) ;
     
     int c1 = conflits_list[2*i+1] ;
     {
         auto iter = labels_set.insert(c1) ;
         //std::cout<<"C[1]"<<c1<<" "<<iter.second<<std::endl ;
         if(iter.second)
         {  
             labels.push_back(c1) ;
         }
     }
     label_conflits[c1].push_back(c_index) ;
     
     ++c_index ;
  }
  
  std::cout<<"NB LABELS : "<<labels.size()<<std::endl ;
  std::cout<<"NB CONFLITS:"<<nb_conflits<<std::endl ;
  
  std::vector<int> ordered_labels ;
  ordered_labels.reserve(labels.size()) ;
  std::set<int> ordered_labels_set ;
  std::size_t ic = 0 ;
  for(int i=0;i<nb_conflits;++i)
  {
     int l = conflits_list[2*i] ;
     ordered_labels.push_back(l) ;
     ordered_labels_set.insert(l) ;
     
     int l1 = conflits_list[2*i+1] ;
     if(l1==l)
     {
        //std::cout<<"INDEPENDANT NODE"<<l<<" "<<l1<<std::endl ;
        ++ic ;
        continue;
     }
     for(auto k : label_conflits[l])
     {
        if(k>ic)
        {
          auto lc0 = conflits_list[2*k  ] ;
          auto lc1 = conflits_list[2*i+1] ;
          if(lc0==l)
          {
            conflits_list[2*k  ] = l1 ;
          }
          else
          {
            conflits_list[2*k+1 ] = l1 ;
          }
          label_conflits[l1].push_back(k) ;
        }
     }
     ++ic ;
  }
  
  std::vector<int> independant_labels ;
  std::map<int,int> new_labels ;
  std::size_t icount = 0 ;
  for(auto l : labels)
  {
        if( ordered_labels_set.find(l) == ordered_labels_set.end())
        {
            independant_labels.push_back(l) ;
            
            res_list[icount++] = l ;
            res_list[icount++] = l ;
            new_labels[l] = l ;
        }
   }

  //std::cout<<"IND LABELS"<<independant_labels<<std::endl ;

  for(int i =0;i<nb_conflits;++i)
  {
        auto c = &conflits_list[2*(nb_conflits - i - 1)] ;
        if(new_labels.find(c[1]) == new_labels.end())
        {
            if(c[1] != c[0])
                std::cout<<"UNXPECTED ERROR"<<c[1]<<"NOT EQUAL"<<c[0]<<std::endl ;
            new_labels[c[1]] = c[1] ;
        }
        res_list[icount++] = c[0] ;
        res_list[icount++] = new_labels[c[1]] ;
        new_labels[c[0]] = new_labels[c[1]] ;
        //std::cout<<"NEW LABELS["<<icount<<","<<c[0]<<"]="<<new_labels[c[1]]<<std::endl;
   }
   int nb_labels = labels.size() ;
   return nb_labels ;
}


int solveV2C(int* conflits_list, int nb_conflits,int* res_list)
{
    std::map<int,int> graph ;
    
  for(int i=0;i<nb_conflits;++i)
  {
     int l0 = conflits_list[2*i] ;
     int l1 = conflits_list[2*i+1] ;
     auto iter0 = graph.find(l0) ;
     std::cout<<" CONFLITS : "<<l0<<" "<<l1<<std::endl ;
     if(iter0 == graph.end())
     {
        // l1 not connected
        auto iter1 = graph.find(l1) ;
        if(iter1 == graph.end())
        {
           graph[l0] = -1 ;
           graph[l1] = l0 ;
        }
        else
        {
          // connect l0 to l1
          graph[l0] = iter1->second ;
        }
     }
     else
     {
        // l0 already
        auto iter1 = graph.find(l1) ;
        if(iter1 == graph.end())
        {
          // connect l1 to l0
          graph[l1] = iter0->second ;
        }
        else
        {
          if(iter0->second!=iter1->second)
          {
              if(iter0->second==-1)
                  iter1->second = l0 ;
              else
                  iter1->second = iter0->second ;
          }
        }
     }
  }
     
 std::size_t icount = 0 ;
 for( auto iter : graph)
 {
     res_list[2*icount  ] = iter.first ;
     int parent = iter.first ;
     int child = iter.second ;
     std::cout<<"ITER ; "<<icount<<" "<<parent<<" "<<child<<std::endl ;
     while(child!=-1)
     {
       parent = child ;
       child = graph[parent] ;
     }
     res_list[2*icount+1 ] = parent ;
     ++icount ;
 }
 int nb_labels = icount ;
 return nb_labels ;
}
