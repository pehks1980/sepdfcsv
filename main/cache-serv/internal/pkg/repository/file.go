package repository

import (
	"context"

	"github.com/pehks1980/cache-serv/internal/pkg/model"
)


type FileRepo struct {
	fileName string
}

func (fr *FileRepo) New (config string) RepoIf{
	// todo init
	return &FileRepo{fileName: "file"}
}

func NewFileRepo(fileName string) *FileRepo {
	return &FileRepo{fileName: fileName}
}

func (fr *FileRepo) Get(getReq string) (string, error) {
	// TODO: impl
	return "", nil
}

func (fr *FileRepo) Put(putReq *model.PutValue) error {
	// TODO: impl
	return nil
}


func (fr *FileRepo) Vacuum(ctx context.Context)  {
	// TODO: impl

}
