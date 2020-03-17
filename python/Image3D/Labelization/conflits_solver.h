#include <iostream>
#include <map>
#include <set>
#include <vector>

int solveC(int* conflits_list, int nb_conflits,int* res_list)
{
  std::cout<<"SOLVE CONFLITS"<<std::endl;
  std::set<int> labels_set ;
  std::map<int,std::vector<int> > label_conflits ;
  std::vector<int> labels ;
  std::size_t c_index = 0 ;
  for(int i=0;i<nb_conflits;++i)
  {
     int c0 = conflits_list[2*i] ;
     {
         auto iter = labels_set.insert(c0) ;
         if(iter->second)
         {  
             labels.push_back(c0) ;
         }
     }
     label_conflits[c0].push_back[c_index] ;
     
     int c1 = conflits_list[2*i+1] ;
     {
         auto iter = labels_set.insert(c1) ;
         if(iter->second)
         {  
             labels.push_back(c1) ;
         }
     }
     label_conflits[c1].push_back[c_index] ;
     
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
        std::cout<<"INDEPENDANT NODE"<<l<<" "<<l1<std::endl ;
        ++ic ;
        continue;
     }
     for(auto k : label_conflits[l])
     {
        if(k>ic)
        {
          lc0 = conflits_list[2*k  ] ;
          lc1 = conflits_list[2*i+1] ;
          if(lc0==l)
          {
            conflits_list[2*k  ] = l1 ;
          }
          else
          {
            conflits_list[2*k+1 ] = l1 ;
          }
          label_conflits[l1].push_back(k)
        }
     }
     ++ic ;
  }
  
  std::vector<int> independant_labels ;
  std::map<int,int> new_labels ;
  for(auto l : labels)
  {
        if( ordered_labels_set.find(l) == ordered_labels_set.end())
        {
            independant_labels.push_back(l) ;
            new_labels[l] = l ;
        }
   }

  std::cout<<"IND LABELS"<<independant_labels<<std::endl ;

  std::size_t icount = 0 ;
  for(int i =0;i<nb_conflits;++i)
  {
        c = &conflits[2*(nb_conflits - i - 1)]
        if(new_labels.find(c[1]) == new_labels.end())
        {
            if(c[1] != c[0])
                std::cout<<"UNXPECTED ERROR"<<c[1]<<"NOT EQUAL"<<c[0]<<std::endl ;
            new_labels[c[1]] = c[1] ;
        }
        res_list[icount++] = c[0] ;
        res_list[icount++] = new_labels[c[1]] ;
        new_labels[c[0]] = new_labels[c[1]] ;
   }
   int nb_labels = labels.size() ;
   return nb_labels ;
}

