# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy .csproj and restore
COPY UserServiceApi/UserServiceApi.csproj UserServiceApi/
RUN dotnet restore UserServiceApi/UserServiceApi.csproj

# Copy everything else and build
COPY . .
WORKDIR /src/UserServiceApi
RUN dotnet publish -c Release -o /app/publish

# Stage 2: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .

# Environment settings (optional)
ENV ASPNETCORE_URLS=http://localhost:5000
EXPOSE 5000

ENTRYPOINT ["dotnet", "UserServiceApi.dll"]