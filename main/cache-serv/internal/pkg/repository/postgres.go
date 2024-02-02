package repository

import (
	"context"
	"github.com/pehks1980/cache-serv/internal/pkg/model"
)

type PgRepo struct{}

type RepoIf interface {
	New(config string) RepoIf
	Get(key string) (string, error)
	Put(putReq *model.PutValue) error
	Vacuum (ctx context.Context)
}

func (pgr *PgRepo) Vacuum(ctx context.Context) {
	// TODO: impl
	
}


func NewPgRepo() *PgRepo {
	return &PgRepo{}
}

func (pgr *PgRepo) New(config string) RepoIf {
	// todo init
	return &PgRepo{}
}

func (pgr *PgRepo) Get(getReq string) (string, error) {
	// TODO: impl
	return "", nil
}

func (pgr *PgRepo) Put(putReq *model.PutValue) error {
	// TODO: impl
	return nil
}
