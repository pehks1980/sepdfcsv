package service

import (
	"log"

	cache_serv "github.com/pehks1980/cache-serv/pkg/cache-serv"
)

func (s *Service) Get(req *cache_serv.GetValueReq) (*cache_serv.GetValueResp, error) {
	value, err := s.repo.Get(req.Key)
	if err != nil {
		log.Printf("service/Get: get from repo err: %v", err)
		return nil, err
	}

	return &cache_serv.GetValueResp{Value: value}, nil
}
